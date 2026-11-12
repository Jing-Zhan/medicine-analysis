from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/overview/", views.overview, name="overview"),
    path("api/province/", views.province, name="province"),
    path("api/drug-top10/", views.drug_top10, name="drug_top10"),
    path("api/drug-amount/", views.drug_amount, name="drug_amount"),
    path("api/disease-top10/", views.disease_top10, name="disease_top10"),
    path("api/relations/", views.relations, name="relations"),
    path("api/health/", views.health, name="health"),
]
