from django.shortcuts import render
from skating import db


@db.database_errors
def rink_list(request):
    return render(request, "rinks/rink_list.html", {"rinks": db.get_rinks()})
