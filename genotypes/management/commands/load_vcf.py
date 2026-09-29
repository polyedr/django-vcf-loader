import gzip
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from genotypes.models import Assembly, Chromosome, Genotype, Sample, Species


class Command(BaseCommand):
    help = "Load genotypes from a VCF or VCF.GZ file"

    batch_size = 5000

    def add_arguments(self, parser):
        parser.add_argument("vcf_file", help="Path to a .vcf or .vcf.gz file")
        parser.add_argument(
            "--species",
            default="Homo sapiens",
            help="Species name (default: Homo sapiens)",
        )
        parser.add_argument(
            "--assembly",
            default="GRCh38",
            help="Genome assembly name (default: GRCh38)",
        )
        parser.add_argument(
            "--sample",
            help="Sample name (default: value from the VCF header)",
        )

    def handle(self, *args, **options):
        file_path = Path(options["vcf_file"])

        if not file_path.is_file():
            raise CommandError(f"File does not exist: {file_path}")

        open_file = gzip.open if file_path.name.endswith(".gz") else open
        batch = []
        total = 0
        header_found = False
        assembly = None
        sample = None
        chromosome_cache = {}

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
                        assembly, sample = self.get_context(columns, options)
                        header_found = True
                        continue

                    if line.startswith("#") or not line.strip():
                        continue

                    if not header_found:
                        raise CommandError("VCF header line #CHROM was not found")

                    genotype = self.parse_line(
                        line,
                        line_number,
                        assembly,
                        sample,
                        chromosome_cache,
                    )
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

    def get_context(self, columns, options):
        species, _ = Species.objects.get_or_create(name=options["species"])
        assembly, _ = Assembly.objects.get_or_create(
            name=options["assembly"],
            species=species,
        )
        sample_name = options["sample"] or columns[9]
        sample, _ = Sample.objects.get_or_create(
            name=sample_name,
            species=species,
        )
        return assembly, sample

    def parse_line(self, line, line_number, assembly, sample, chromosome_cache):
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

        chromosome_name = columns[0]
        chromosome = chromosome_cache.get(chromosome_name)

        if chromosome is None:
            chromosome, _ = Chromosome.objects.get_or_create(
                name=chromosome_name,
                assembly=assembly,
            )
            chromosome_cache[chromosome_name] = chromosome

        return Genotype(
            chromosome=chromosome,
            sample=sample,
            position=position,
            ref=columns[3],
            alt=columns[4],
            gt=gt,
        )
