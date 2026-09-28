import gzip
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from genotypes.models import Genotype


class LoadVcfCommandTests(TestCase):
    fixture_path = Path(settings.BASE_DIR) / "genotypes" / "fixtures" / "tiny.vcf"

    def test_loads_plain_vcf(self):
        call_command("load_vcf", self.fixture_path)

        self.assertEqual(Genotype.objects.count(), 10)

        genotype = Genotype.objects.get(chromosome="chr1", position=784102)
        self.assertEqual(genotype.ref, "G")
        self.assertEqual(genotype.alt, "A,C")
        self.assertEqual(genotype.gt, "1/2")

    def test_loads_gzipped_vcf(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            gzip_path = Path(temp_directory) / "tiny.vcf.gz"
            content = self.fixture_path.read_text(encoding="utf-8")

            with gzip.open(gzip_path, "wt", encoding="utf-8") as gzip_file:
                gzip_file.write(content)

            call_command("load_vcf", gzip_path)

        self.assertEqual(Genotype.objects.count(), 10)


class GenotypeApiTests(APITestCase):
    def setUp(self):
        Genotype.objects.create(
            chromosome="chr1",
            position=783006,
            ref="A",
            alt="G",
            gt="0/1",
        )
        Genotype.objects.create(
            chromosome="chr2",
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
