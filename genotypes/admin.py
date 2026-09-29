from django.contrib import admin

from genotypes.models import Assembly, Chromosome, Genotype, Sample, Species


admin.site.register(Species)
admin.site.register(Assembly)
admin.site.register(Chromosome)
admin.site.register(Sample)
admin.site.register(Genotype)
