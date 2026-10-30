from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("rinks/", include("rinks.urls")),
    path("skating/", include("skating.urls")),
]
