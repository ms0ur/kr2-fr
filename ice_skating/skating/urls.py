from django.urls import path
from . import views

app_name = "skating"
urlpatterns = [
    path("", views.skate_list, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<slug:slug>/", views.skate_detail, name="detail"),
]
