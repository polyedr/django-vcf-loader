import gzip
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from genotypes.models import Assembly, Chromosome, Genotype, Sample, Species


class LoadVcfCommandTests(TestCase):
    fixture_path = Path(settings.BASE_DIR) / "genotypes" / "fixtures" / "tiny.vcf"

    def test_loads_plain_vcf(self):
        call_command("load_vcf", self.fixture_path)

        self.assertEqual(Genotype.objects.count(), 10)

        genotype = Genotype.objects.get(
            chromosome__name="chr1",
            position=784102,
        )
        self.assertEqual(genotype.ref, "G")
        self.assertEqual(genotype.alt, "A,C")
        self.assertEqual(genotype.gt, "1/2")
        self.assertEqual(genotype.sample.name, "HG001")
        self.assertEqual(genotype.chromosome.assembly.name, "GRCh38")
        self.assertEqual(Species.objects.count(), 1)
        self.assertEqual(Assembly.objects.count(), 1)
        self.assertEqual(Chromosome.objects.count(), 7)
        self.assertEqual(Sample.objects.count(), 1)

    def test_loads_gzipped_vcf(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            gzip_path = Path(temp_directory) / "tiny.vcf.gz"
            content = self.fixture_path.read_text(encoding="utf-8")

            with gzip.open(gzip_path, "wt", encoding="utf-8") as gzip_file:
                gzip_file.write(content)

            call_command("load_vcf", gzip_path)

        self.assertEqual(Genotype.objects.count(), 10)

    def test_reuses_relations_for_different_samples(self):
        call_command("load_vcf", self.fixture_path, sample="HG001")
        call_command("load_vcf", self.fixture_path, sample="HG002")

        self.assertEqual(Genotype.objects.count(), 20)
        self.assertEqual(Species.objects.count(), 1)
        self.assertEqual(Assembly.objects.count(), 1)
        self.assertEqual(Chromosome.objects.count(), 7)
        self.assertEqual(Sample.objects.count(), 2)


class GenotypeApiTests(APITestCase):
    def setUp(self):
        species = Species.objects.create(name="Homo sapiens")
        assembly = Assembly.objects.create(name="GRCh38", species=species)
        sample = Sample.objects.create(name="HG001", species=species)
        chromosome_1 = Chromosome.objects.create(
            name="chr1",
            assembly=assembly,
        )
        chromosome_2 = Chromosome.objects.create(
            name="chr2",
            assembly=assembly,
        )
        Genotype.objects.create(
            chromosome=chromosome_1,
            sample=sample,
            position=783006,
            ref="A",
            alt="G",
            gt="0/1",
        )
        Genotype.objects.create(
            chromosome=chromosome_2,
            sample=sample,
            position=10500,
            ref="T",
            alt="C",
            gt="1/1",
        )
        self.url = reverse("get-genotypes")

    def test_returns_all_genotypes(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filters_by_chromosome_and_coordinate(self):
        response = self.client.get(
            self.url,
            {"chromosome": "chr1", "coordinate": 783006},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sample"], "HG001")
        self.assertEqual(response.data[0]["chromosome"], "chr1")
        self.assertEqual(response.data[0]["coordinate"], 783006)

    def test_returns_empty_list_when_genotype_does_not_exist(self):
        response = self.client.get(
            self.url,
            {"chromosome": "chr99", "coordinate": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_rejects_invalid_coordinate(self):
        response = self.client.get(self.url, {"coordinate": "unknown"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["coordinate"], "Must be an integer.")
