from django.shortcuts import render
from skating import db


@db.database_errors
def home(request):
    return render(request, "homepage/home.html", {"total": db.get_count()})
