import gzip
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from genotypes.models import Genotype


class Command(BaseCommand):
    help = "Load genotypes from a VCF or VCF.GZ file"

    batch_size = 5000

    def add_arguments(self, parser):
        parser.add_argument("vcf_file", help="Path to a .vcf or .vcf.gz file")

    def handle(self, *args, **options):
        file_path = Path(options["vcf_file"])

        if not file_path.is_file():
            raise CommandError(f"File does not exist: {file_path}")

        open_file = gzip.open if file_path.name.endswith(".gz") else open
        batch = []
        total = 0
        header_found = False

        try:
            with open_file(file_path, mode="rt", encoding="utf-8") as vcf_file:
                for line_number, line in enumerate(vcf_file, start=1):
                    if line.startswith("##"):
                        continue

                    if line.startswith("#CHROM"):
                        columns = line.rstrip("\n").split("\t")
                        if len(columns) < 10:
                            raise CommandError(
                                "VCF must contain FORMAT and at least one sample column"
                            )
                        header_found = True
                        continue

                    if line.startswith("#") or not line.strip():
                        continue

                    if not header_found:
                        raise CommandError("VCF header line #CHROM was not found")

                    genotype = self.parse_line(line, line_number)
                    batch.append(genotype)

                    if len(batch) >= self.batch_size:
                        Genotype.objects.bulk_create(batch, batch_size=self.batch_size)
                        total += len(batch)
                        batch.clear()

                if batch:
                    Genotype.objects.bulk_create(batch, batch_size=self.batch_size)
                    total += len(batch)

        except (OSError, UnicodeError) as error:
            raise CommandError(f"Could not read {file_path}: {error}") from error

        if not header_found:
            raise CommandError("VCF header line #CHROM was not found")

        self.stdout.write(
            self.style.SUCCESS(f"Loaded {total} genotypes from {file_path}")
        )

    def parse_line(self, line, line_number):
        columns = line.rstrip("\n").split("\t")

        if len(columns) < 10:
            raise CommandError(
                f"Invalid VCF row at line {line_number}: expected at least 10 columns"
            )

        try:
            position = int(columns[1])
        except ValueError as error:
            raise CommandError(
                f"Invalid position at line {line_number}: {columns[1]}"
            ) from error

        format_keys = columns[8].split(":")
        sample_values = columns[9].split(":")
        gt = "."

        if "GT" in format_keys:
            gt_index = format_keys.index("GT")
            if gt_index < len(sample_values):
                gt = sample_values[gt_index]

        return Genotype(
            chromosome=columns[0],
            position=position,
            ref=columns[3],
            alt=columns[4],
            gt=gt,
        )
