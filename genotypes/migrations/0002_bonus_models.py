import django.db.models.deletion
from django.db import migrations, models


def add_relations_to_existing_genotypes(apps, schema_editor):
    Species = apps.get_model("genotypes", "Species")
    Assembly = apps.get_model("genotypes", "Assembly")
    Chromosome = apps.get_model("genotypes", "Chromosome")
    Sample = apps.get_model("genotypes", "Sample")
    Genotype = apps.get_model("genotypes", "Genotype")

    if not Genotype.objects.exists():
        return

    species = Species.objects.create(name="Homo sapiens")
    assembly = Assembly.objects.create(name="GRCh38", species=species)
    sample = Sample.objects.create(name="HG001", species=species)

    chromosome_names = (
        Genotype.objects.order_by()
        .values_list("chromosome_name", flat=True)
        .distinct()
    )

    for chromosome_name in chromosome_names:
        chromosome = Chromosome.objects.create(
            name=chromosome_name,
            assembly=assembly,
        )
        Genotype.objects.filter(chromosome_name=chromosome_name).update(
            chromosome=chromosome,
            sample=sample,
        )


def restore_chromosome_names(apps, schema_editor):
    Chromosome = apps.get_model("genotypes", "Chromosome")
    Genotype = apps.get_model("genotypes", "Genotype")

    for chromosome in Chromosome.objects.all():
        Genotype.objects.filter(chromosome=chromosome).update(
            chromosome_name=chromosome.name,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("genotypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Species",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, unique=True)),
            ],
            options={
                "verbose_name_plural": "species",
            },
        ),
        migrations.CreateModel(
            name="Assembly",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assemblies",
                        to="genotypes.species",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "assemblies",
            },
        ),
        migrations.CreateModel(
            name="Chromosome",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=32)),
                (
                    "assembly",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chromosomes",
                        to="genotypes.assembly",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Sample",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="samples",
                        to="genotypes.species",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="assembly",
            constraint=models.UniqueConstraint(
                fields=("name", "species"),
                name="unique_assembly_per_species",
            ),
        ),
        migrations.AddConstraint(
            model_name="chromosome",
            constraint=models.UniqueConstraint(
                fields=("name", "assembly"),
                name="unique_chromosome_per_assembly",
            ),
        ),
        migrations.AddConstraint(
            model_name="sample",
            constraint=models.UniqueConstraint(
                fields=("name", "species"),
                name="unique_sample_per_species",
            ),
        ),
        migrations.RemoveIndex(
            model_name="genotype",
            name="genotype_chr_pos_idx",
        ),
        migrations.RenameField(
            model_name="genotype",
            old_name="chromosome",
            new_name="chromosome_name",
        ),
        migrations.AlterField(
            model_name="genotype",
            name="chromosome_name",
            field=models.CharField(default="", max_length=32),
        ),
        migrations.AddField(
            model_name="genotype",
            name="chromosome",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="genotypes",
                to="genotypes.chromosome",
            ),
        ),
        migrations.AddField(
            model_name="genotype",
            name="sample",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="genotypes",
                to="genotypes.sample",
            ),
        ),
        migrations.RunPython(
            add_relations_to_existing_genotypes,
            restore_chromosome_names,
        ),
        migrations.RemoveField(
            model_name="genotype",
            name="chromosome_name",
        ),
        migrations.AlterField(
            model_name="genotype",
            name="chromosome",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="genotypes",
                to="genotypes.chromosome",
            ),
        ),
        migrations.AlterField(
            model_name="genotype",
            name="sample",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="genotypes",
                to="genotypes.sample",
            ),
        ),
        migrations.AddIndex(
            model_name="genotype",
            index=models.Index(
                fields=["chromosome", "position"],
                name="genotype_chr_pos_idx",
            ),
        ),
    ]
