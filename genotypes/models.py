from django.db import models


class Genotype(models.Model):
    chromosome = models.CharField(max_length=32)
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
        return f"{self.chromosome}:{self.position} {self.ref}>{self.alt} {self.gt}"
