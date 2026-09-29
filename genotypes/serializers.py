from rest_framework import serializers

from genotypes.models import Genotype


class GenotypeSerializer(serializers.ModelSerializer):
    chromosome = serializers.CharField(source="chromosome.name", read_only=True)
    coordinate = serializers.IntegerField(source="position", read_only=True)
    sample = serializers.CharField(source="sample.name", read_only=True)

    class Meta:
        model = Genotype
        fields = [
            "id",
            "sample",
            "chromosome",
            "coordinate",
            "ref",
            "alt",
            "gt",
        ]
