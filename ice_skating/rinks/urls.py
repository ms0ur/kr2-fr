from django.urls import path
from . import views

app_name = "rinks"
urlpatterns = [path("", views.rink_list, name="list")]
