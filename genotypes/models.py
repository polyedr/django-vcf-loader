from django.db import models


class Species(models.Model):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name_plural = "species"

    def __str__(self):
        return self.name


class Assembly(models.Model):
    name = models.CharField(max_length=128)
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="assemblies",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "species"],
                name="unique_assembly_per_species",
            ),
        ]
        verbose_name_plural = "assemblies"

    def __str__(self):
        return f"{self.species}: {self.name}"


class Chromosome(models.Model):
    name = models.CharField(max_length=32)
    assembly = models.ForeignKey(
        Assembly,
        on_delete=models.CASCADE,
        related_name="chromosomes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "assembly"],
                name="unique_chromosome_per_assembly",
            ),
        ]

    def __str__(self):
        return f"{self.assembly.name}: {self.name}"


class Sample(models.Model):
    name = models.CharField(max_length=128)
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name="samples",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "species"],
                name="unique_sample_per_species",
            ),
        ]

    def __str__(self):
        return self.name


class Genotype(models.Model):
    chromosome = models.ForeignKey(
        Chromosome,
        on_delete=models.CASCADE,
        related_name="genotypes",
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name="genotypes",
    )
    position = models.PositiveBigIntegerField()
    ref = models.TextField()
    alt = models.TextField()
    gt = models.CharField(max_length=64)

    class Meta:
        indexes = [
            models.Index(
                fields=["chromosome", "position"],
                name="genotype_chr_pos_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.sample} {self.chromosome.name}:{self.position} "
            f"{self.ref}>{self.alt} {self.gt}"
        )
