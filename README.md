# Django VCF loader

Тестовый Django-проект для загрузки генотипов из VCF-файла GIAB и получения
данных через REST API.

## Стек

- Python 3.11
- Django 5.1
- Django REST Framework
- SQLite
- conda/mamba/micromamba

BioPython не используется. VCF читается построчно стандартными средствами
Python, сжатые файлы открываются через `gzip`.

## Установка

Создайте и активируйте окружение:

```bash
mamba env create -f env.yml
mamba activate test-task-django
```

Вместо `mamba` можно использовать `conda` или `micromamba`.

Примените миграции:

```bash
python manage.py migrate
```

## Загрузка VCF

Скачайте файл GIAB:

```bash
wget https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/NA12878_HG001/latest/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
```

Загрузите его в базу:

```bash
python manage.py load_vcf HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz
```

Команда принимает как `.vcf`, так и `.vcf.gz`. Для быстрой проверки можно
использовать маленький файл из репозитория:

```bash
python manage.py load_vcf genotypes/fixtures/tiny.vcf
```

## Запуск

```bash
python manage.py runserver
```

Пример API-запроса:

```text
http://127.0.0.1:8000/api/get_genotypes/?chromosome=chr1&coordinate=783006
```

Параметры `chromosome` и `coordinate` можно использовать вместе или по
отдельности. Без параметров endpoint возвращает все записи.

Пример ответа:

```json
[
  {
    "id": 1,
    "chromosome": "chr1",
    "coordinate": 783006,
    "ref": "A",
    "alt": "G",
    "gt": "0/1"
  }
]
```

## Тесты

```bash
python manage.py test
```

Тесты используют только маленький VCF и не загружают полный файл GIAB.
