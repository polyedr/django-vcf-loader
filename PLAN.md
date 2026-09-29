# План работ: test-task-django

## Согласованный стек

- Python 3.11
- Django 5.1
- Django REST Framework
- SQLite
- conda/mamba/micromamba, окружение `test-task-django`
- зависимости в `env.yml`
- без Docker и BioPython
- Полный VCF в git и в индекс Cursor не кладём (есть `.cursorignore`)

## Объём данных

- GIAB HG001, GRCh38, ~3.89 млн вариантов
- В модель — только нужные поля, не весь INFO
- Разработка и тесты — на маленьком фикстурном VCF
- Полный `.vcf.gz` — один финальный прогон `load_vcf`

---

## 0. Гигиена репозитория

- [x] `.cursorignore` (VCF, sqlite, venv)
- [x] `.gitignore`: VCF, sqlite, venv, `__pycache__`, `.env`
- [x] Не коммитить `HG001_*.vcf` и `.vcf.gz`
- [x] Распакованный 2 ГБ `.vcf` удалён — загрузка проверена на `.vcf.gz`

## 1. Окружение и каркас

- [x] `env.yml`: Python 3.11, Django 5.1, Django REST Framework
- [x] Проверить создание окружения: `mamba env create -f env.yml`
- [x] `django-admin startproject` + одно приложение `genotypes`
- [x] SQLite по умолчанию, `DEBUG=True` для локальной проверки

## 2. Модели и миграции

Минимум (обязательно по ТЗ):

- [x] `Genotype`: chromosome, position, ref, alt, gt
- [x] Индекс `(chromosome, position)` под API-фильтр

Бонус (если останется время) — отдельные модели и связи:

- [x] `Species`, `Assembly`, `Chromosome`, `Sample`
- [x] `Coordinate` / `Allele` не добавляем, чтобы не раздувать загрузку;
      chromosome+position остаются в `Genotype`, связи сделаны через
      Sample/Assembly/Chromosome

## 3. Команда `load_vcf`

- [x] `python manage.py load_vcf <файл>`
- [x] Поддержка `.vcf` и `.vcf.gz` (в ТЗ грузят gz)
- [x] Парсер как текстовой таблицы: пропуск `#`, колонки CHROM/POS/REF/ALT/FORMAT+sample
- [x] Извлекать GT по его позиции в `FORMAT`, INFO целиком не сохранять
- [x] `bulk_create` пачками по 5 тысяч строк
- [x] Фикстура `fixtures/tiny.vcf` на 10 вариантов для отладки

## 4. API

- [x] DRF: класс `GenotypeSerializer`, class-based View `ListAPIView`
- [x] URL: `/api/get_genotypes/`
- [x] Фильтры query: `chromosome`, `coordinate` (как в примере ТЗ)
- [x] Проверка: `http://127.0.0.1:8000/api/get_genotypes/?chromosome=chr1&coordinate=783006`
      (в PDF порт не указан — в README указать 8000)

## 5. Тесты

- [x] Загрузка `tiny.vcf` и `.vcf.gz` через `load_vcf`
- [x] API: есть запись, нет записи, фильтр по хромосоме/позиции
- [x] Полный HG001 в тестах не использовать

## 6. README и сдача

- [x] Команды как в PDF, но рабочие: `manage.py`, порт 8000
- [x] Создание окружения через conda/mamba из `env.yml`
- [x] Указать согласованные версии Django 5.1 и Python 3.11
- [ ] Репозиторий на GitHub (без VCF и sqlite)

## 7. Финальная проверка

- [x] `migrate` на чистой SQLite
- [x] `load_vcf` на `tiny.vcf`
- [x] `load_vcf` на полном `.vcf.gz`: 3 893 341 строк;
      бонусная схема со связями — 2 мин 15 с
- [x] Запрос из ТЗ через HTTP
- [x] Прогнать тесты

---

## Порядок выполнения

1 → 2 → 3 (на tiny.vcf) → 4 → 5 → бонус по желанию → 6 → 7.

Не начинать с полного GIAB: сначала команда и API на 20 строках.
