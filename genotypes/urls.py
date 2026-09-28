from django.urls import path

from genotypes.views import GenotypeListView


urlpatterns = [
    path("get_genotypes/", GenotypeListView.as_view(), name="get-genotypes"),
]
