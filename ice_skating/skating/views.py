from django.http import Http404
from django.shortcuts import render
from . import db


def integer_parameter(request, name, default, minimum, maximum):
    raw = request.GET.get(name, "")
    value = default if raw == "" else int(raw)
    if not minimum <= value <= maximum:
        raise ValueError
    return value


@db.database_errors
def skate_list(request):
    try:
        skaters = integer_parameter(request, "skaters", 0, 0, 1000000000)
        limit = integer_parameter(request, "limit", 100, 1, 1000)
        sort = request.GET.get("sort", "date")
        if sort not in db.SORT_OPTIONS:
            raise ValueError
    except ValueError:
        return render(request, "error.html", {
            "message": "Проверьте параметры: посетители — целое число от 0 до 1 000 000 000, "
                       "лимит — от 1 до 1000. Выберите сортировку из списка."
        }, status=400)
    return render(request, "skating/skate_list.html", {
        "sessions": db.get_sessions(skaters, sort, limit),
        "skaters": skaters, "limit": limit, "sort": sort,
        "sort_options": [(key, value[1]) for key, value in db.SORT_OPTIONS.items()],
    })


@db.database_errors
def skate_detail(request, slug):
    session = db.get_session(slug)
    if session is None:
        raise Http404("Сеанс не найден")
    return render(request, "skating/skate_detail.html", {"session": session})


@db.database_errors
def statistics(request):
    return render(request, "skating/statistics.html", {
        "statistics": db.get_statistics(2), "min_count": 2, "total": db.get_count(),
    })
