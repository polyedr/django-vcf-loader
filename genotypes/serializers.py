from rest_framework import serializers

from genotypes.models import Genotype


class GenotypeSerializer(serializers.ModelSerializer):
    coordinate = serializers.IntegerField(source="position", read_only=True)

    class Meta:
        model = Genotype
        fields = ["id", "chromosome", "coordinate", "ref", "alt", "gt"]
