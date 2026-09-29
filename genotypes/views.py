from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView

from genotypes.models import Genotype
from genotypes.serializers import GenotypeSerializer


class GenotypeListView(ListAPIView):
    serializer_class = GenotypeSerializer

    def get_queryset(self):
        queryset = Genotype.objects.select_related(
            "chromosome__assembly",
            "sample__species",
        ).order_by("id")
        species = self.request.query_params.get("species")
        assembly = self.request.query_params.get("assembly")
        sample = self.request.query_params.get("sample")
        chromosome = self.request.query_params.get("chromosome")
        coordinate = self.request.query_params.get("coordinate")

        if species:
            queryset = queryset.filter(sample__species__name=species)

        if assembly:
            queryset = queryset.filter(chromosome__assembly__name=assembly)

        if sample:
            queryset = queryset.filter(sample__name=sample)

        if chromosome:
            queryset = queryset.filter(chromosome__name=chromosome)

        if coordinate:
            try:
                position = int(coordinate)
            except ValueError as error:
                raise ValidationError(
                    {"coordinate": "Must be an integer."}
                ) from error
            queryset = queryset.filter(position=position)

        return queryset
