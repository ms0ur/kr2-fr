# Контрольная работа № 2 — ответы на все теоретические вопросы

**Дисциплина:** «Технологии разработки приложений на базе фреймворков»  
**Количество вопросов:** 30 (15 — шаблоны Django, 15 — базы данных и ORM Django)  
**Ориентир по версиям:** Django 5.0–5.2.

Материал организован в той же последовательности, что и вопросы в исходном файле «КР2_теоретические вопросы.pdf». Для каждого вопроса приведены пояснения и примеры кода. Код отдельных вопросов является самостоятельным примером: названия классов и настройки в разных фрагментах не обязательно образуют один запускаемый проект.

## Содержание

- [Часть I. Шаблоны Django](#часть-i-шаблоны-django)
  - [1. render_to_string() и render()](#i-1-rendertostring-и-render)
  - [2. Настройка TEMPLATES](#i-2-настройка-templates)
  - [3. Передача контекста в шаблон](#i-3-передача-контекста-в-шаблон)
  - [4. Стандартные фильтры и цепочки](#i-4-стандартные-фильтры-и-цепочки)
  - [5. default и default_if_none](#i-5-default-и-default_if_none)
  - [6. Автоэкранирование HTML](#i-6-автоэкранирование-html)
  - [7. Фильтры в Python-коде](#i-7-фильтры-в-python-коде)
  - [8. Переменная forloop](#i-8-переменная-forloop)
  - [9. Тег if](#i-9-тег-if)
  - [10. Тег url и reverse()](#i-10-тег-url-и-reverse)
  - [11. Тег querystring](#i-11-тег-querystring)
  - [12. Наследование шаблонов](#i-12-наследование-шаблонов)
  - [13. Тег include](#i-13-тег-include)
  - [14. Статические файлы](#i-14-статические-файлы)
  - [15. Пользовательские шаблонные теги](#i-15-пользовательские-шаблонные-теги)
- [Часть II. Базы данных и ORM Django](#часть-ii-базы-данных-и-orm-django)
  - [1. Основы ORM](#ii-1-основы-orm)
  - [2. Поля модели](#ii-2-поля-модели)
  - [3. Новшества Django 5.0–5.2](#ii-3-новшества-django-50–52)
  - [4. Миграции](#ii-4-миграции)
  - [5. Создание записей](#ii-5-создание-записей)
  - [6. Изменение и удаление](#ii-6-изменение-и-удаление)
  - [7. filter() и get()](#ii-7-filter-и-get)
  - [8. Fields lookups](#ii-8-fields-lookups)
  - [9. order_by()](#ii-9-order_by)
  - [10. Слаги](#ii-10-слаги)
  - [11. get_absolute_url()](#ii-11-get_absolute_url)
  - [12. Менеджеры и IntegerChoices](#ii-12-менеджеры-и-integerchoices)
  - [13. ForeignKey и on_delete](#ii-13-foreignkey-и-on_delete)
  - [14. Обратные связи many-to-one](#ii-14-обратные-связи-many-to-one)
  - [15. ManyToManyField и OneToOneField](#ii-15-manytomanyfield-и-onetoonefield)

---

# Часть I. Шаблоны Django

## I. 1. `render_to_string()` и `render()`

Обе функции отображают шаблон Django с подстановкой данных, но возвращают **разные типы результатов**:

- `render_to_string()` из `django.template.loader` возвращает готовую HTML-строку (`str`). HTTP-ответ нужно создать отдельно.
- `render()` из `django.shortcuts` сразу возвращает `HttpResponse` и потому обычно используется непосредственно в представлениях.

**Вариант 1 — `render_to_string()` с явным `HttpResponse`:**

```python
from django.http import HttpResponse
from django.template.loader import render_to_string


def index(request):
    html = render_to_string(
        'women/index.html',
        {'title': 'Главная страница'},
        request=request,
    )
    return HttpResponse(html)
```

**Вариант 2 — `render()`:**

```python
from django.shortcuts import render


def index(request):
    return render(request, 'women/index.html', {
        'title': 'Главная страница',
    })
```

**Почему делают `templates/women/index.html`, а не просто `templates/index.html`?**

Движок ищет шаблоны по относительному пути. Если два приложения содержат файл `templates/index.html`, Django выберет первый найденный шаблон согласно порядку поиска. Подкаталог с именем приложения образует подобие пространства имён:

```text
women/templates/women/index.html
blog/templates/blog/index.html
```

Поэтому `women/index.html` и `blog/index.html` не конфликтуют.

## I. 2. Настройка `TEMPLATES`

В `settings.py` параметр `TEMPLATES` содержит список конфигураций движков шаблонизации. Основные ключи:

- **`BACKEND`** — используемый движок, например встроенный `DjangoTemplates`.
- **`DIRS`** — явные каталоги, где ищутся шаблоны.
- **`APP_DIRS`** — разрешение искать шаблоны в подкаталогах `templates` установленных приложений.
- **`OPTIONS`** — дополнительные параметры, включая контекстные процессоры.

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

**Порядок поиска** при использовании стандартных загрузчиков: сначала каталоги из `DIRS` (в указанном порядке), затем каталоги `templates` приложений из `INSTALLED_APPS` (в порядке регистрации приложений).

Если установить `APP_DIRS=False`, Django перестанет автоматически искать шаблоны внутри приложений. Когда нужного файла нет в `DIRS`, при обращении к странице, использующей такой шаблон, возникнет `TemplateDoesNotExist`. Исправление: включить `APP_DIRS=True` **или** добавить необходимый путь в `DIRS` (либо явно настроить загрузчики).

**Два условия автоматического обнаружения шаблонов приложения:**

1. Приложение зарегистрировано в `INSTALLED_APPS`.
2. Для встроенного движка указано `APP_DIRS=True`.

Также файл должен физически находиться внутри каталога `templates` этого приложения.

## I. 3. Передача контекста в шаблон

Представление передаёт данные шаблону в **словаре контекста**. Имена ключей становятся именами переменных шаблона. Передавать можно строки, числа, списки, словари, объекты Python, модели, QuerySet и другие значения.

Доступ к свойствам и элементам в Django Templates осуществляется через **точечную нотацию**, а не произвольные Python-выражения в квадратных скобках:

```django
{{ title }}
{{ obj.name }}
{{ data.key }}
{{ menu.0.title }}
```

Квадратные скобки (`menu[0]`, `data['key']`) не входят в синтаксис языка шаблонов Django. Если переменная не была передана, по умолчанию выводится пустая строка (это можно изменить настройкой `string_if_invalid`).

**Представление:**

```python
from types import SimpleNamespace
from django.shortcuts import render


def index(request):
    data = {
        'title': 'Главная страница',
        'menu': [
            {'title': 'Главная', 'url': '/'},
            {'title': 'О сайте', 'url': '/about/'},
        ],
        'obj': SimpleNamespace(name='Django', version='5.2'),
    }
    return render(request, 'women/index.html', data)
```

**`women/index.html`:**

```django
<h1>{{ title }}</h1>
<p>Фреймворк: {{ obj.name }}</p>
<p>Версия: {{ obj.version }}</p>

<ul>
    {% for item in menu %}
        <li><a href="{{ item.url }}">{{ item.title }}</a></li>
    {% endfor %}
</ul>
```

## I. 4. Стандартные фильтры и цепочки

Фильтр преобразует значение переменной при отображении:

```django
{{ value|filter }}
{{ value|filter:"argument" }}
{{ value|filter1|filter2 }}
```

Фильтры в цепочке выполняются **слева направо**. Аргумент записывается в кавычках, если это строковый литерал. Без кавычек его можно интерпретировать как имя переменной из контекста.

```django
{{ title|cut:" "|cut:"?" }}
```

Если `title = "Что такое Django?"`, сначала удаляются пробелы, затем вопросительные знаки. Результат: `ЧтотакоеDjango`.

**Комбинация `slugify` и `upper`:**

```django
{{ title|slugify|upper }}
```

Для `title = "The Main Page"`:

```text
Исходное значение: The Main Page
После slugify:    the-main-page
После upper:      THE-MAIN-PAGE
```

## I. 5. `default` и `default_if_none`

`default` подставляет резервное значение, если исходное является *ложным* в смысле Python: `None`, `False`, `0`, `""`, пустой список и так далее.

`default_if_none` подставляет резервное значение **только при `None`**. Пустая строка не вызывает замену.

```django
<h1>{{ main_title|default:"Без заголовка" }}</h1>
<p>{{ value|default_if_none:"Не указано" }}</p>
```

| Исходное состояние соответствующей переменной | `main_title\|default:"Без заголовка"` | `value\|default_if_none:"Не указано"` |
|---|---|---|
| Отсутствует в контексте | `Без заголовка` | Пустая строка |
| Равна `""` | `Без заголовка` | Пустая строка |
| Равна `None` | `Без заголовка` | `Не указано` |

**Примеры контекстов:**

```python
context1 = {}  # Оба значения отсутствуют
context2 = {'main_title': '', 'value': ''}
context3 = {'main_title': None, 'value': None}
```

Для отсутствующей переменной стандартная обработка приводит к пустой строке, поэтому `default_if_none` не рассматривает её как `None`.

## I. 6. Автоэкранирование HTML

Django по умолчанию HTML-экранирует выводимые значения: `<`, `>`, `&`, кавычки заменяются безопасными HTML-сущностями. Например, переданная строка `<script>alert("XSS")</script>` должна отображаться как текст, а не исполняться браузером. Это важная защита от **XSS**.

Отключить автоматическое экранирование можно так:

```django
{% autoescape off %}
    {{ article.content }}
{% endautoescape %}
```

Так можно вывести заранее подготовленную HTML-разметку, но **недоверенный пользовательский HTML выводить без очистки нельзя**.

**Описание статьи с двумя фильтрами:**

```django
{% autoescape off %}
    {{ article.content|truncatewords:30|linebreaks }}
{% endautoescape %}
```

- `truncatewords:30` ограничивает текст 30 словами.
- `linebreaks` преобразует переносы строк в HTML-абзацы и `<br>`.

Однако отключение экранирования небезопасно для пользовательского содержимого. Более безопасный вариант для текста без разрешённой HTML-разметки:

```django
{% autoescape off %}
    {{ article.content|truncatewords:30|escape|linebreaks }}
{% endautoescape %}
```

Фильтр `escape` экранирует текст до создания разметки абзацев. Когда HTML от пользователя действительно должен поддерживаться, требуется специализированная очистка разрешённых тегов и атрибутов.

**Экранирование элементов списка:**

```django
{% autoescape off %}
    {{ items|escapeseq|join:", " }}
{% endautoescape %}
```

`escapeseq` экранирует элементы последовательности по отдельности (добавлен в Django 5.0). Также существуют `force_escape` и `striptags`, однако один лишь `striptags` не гарантирует защиты от XSS.

## I. 7. Фильтры в Python-коде

Стандартные шаблонные фильтры Django размещены в `django.template.defaultfilters`; некоторые имеют реализации в других модулях и могут импортироваться оттуда.

```python
from django.shortcuts import render
from django.template.defaultfilters import slugify


def index(request):
    title = 'The Main Page'
    data = {
        'title': title,
        'slug': slugify(title),
    }
    return render(request, 'women/index.html', data)
```

**Шаблон:**

```django
<h1>{{ title }}</h1>
<p>Slug: {{ slug }}</p>
```

**Результат:** `The Main Page` и `Slug: the-main-page`.

Применение фильтра в Python удобно, когда преобразованное значение нужно использовать в нескольких местах: при формировании контекста, построении структур данных, в бизнес-логике. Для непосредственного получения слага в Python также есть `django.utils.text.slugify`.

## I. 8. Переменная `forloop`

Внутри `{% for %}` Django предоставляет объект `forloop`:

| Свойство | Значение |
|---|---|
| `forloop.counter` | Номер итерации с 1 |
| `forloop.counter0` | Номер итерации с 0 |
| `forloop.revcounter` | Осталось итераций, включая текущую |
| `forloop.revcounter0` | Осталось итераций после текущей |
| `forloop.first` | `True` на первой итерации |
| `forloop.last` | `True` на последней итерации |
| `forloop.parentloop` | Объект `forloop` внешнего цикла |

**Нумерация с единицы и с нуля:**

```django
{% for p in posts %}
    <p>
        Номер {{ forloop.counter }},
        индекс {{ forloop.counter0 }}: {{ p.title }}
    </p>
{% endfor %}
```

**Вложенные циклы:**

```django
{% for category in categories %}
    {% for post in category.posts.all %}
        Категория №{{ forloop.parentloop.counter }},
        статья №{{ forloop.counter }}
    {% endfor %}
{% endfor %}
```

**Разделитель после каждого элемента, кроме последнего:**

```django
{% for p in posts %}
    <h2>{{ p.title }}</h2>
    {% if not forloop.last %}
        <hr>
    {% endif %}
{% endfor %}
```

## I. 9. Тег `if`

Условный тег `{% if %}` позволяет включать или исключать HTML-фрагменты при рендеринге. Поддерживаются операторы `and`, `or`, `not`, сравнения `==`, `!=`, `<`, `>`, `<=`, `>=`, а также `in`, `not in`, `is`, `is not`. Есть ветки `elif` и `else`. Скобками группировать выражения в шаблонном `if` нельзя — сложные проверки лучше заранее подготовить в Python.

**Только опубликованные статьи:**

```django
{% for p in posts %}
    {% if p.is_published %}
        <h2>{{ p.title }}</h2>
        <p>{{ p.content }}</p>
    {% endif %}
{% endfor %}
```

**Составное условие:**

```django
{% if p.is_published and p.views > 100 %}
    <p>Популярная опубликованная статья</p>
{% elif p.is_published %}
    <p>Обычная опубликованная статья</p>
{% else %}
    <p>Черновик</p>
{% endif %}
```

**Чем теги Django отличаются от HTML?**

Теги шаблонизатора (`{% if %}`, `{% for %}`) обрабатываются **на сервере** и не отправляются браузеру. HTML-теги (`<div>`, `<p>`, `<h1>`) отправляются в готовой странице и интерпретируются **на стороне клиента (в браузере)**.

## I. 10. Тег `url` и `reverse()`

Запись пути напрямую в `href`, например `<a href="/post/11/">`, — **жёсткое кодирование (hardcoding)**. Если структура адресов поменяется, придётся искать и исправлять все такие ссылки.

Django позволяет назвать маршрут через аргумент `name` и получать адрес по имени.

**`urls.py`:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:post_id>/', views.show_post, name='post'),
]
```

**Python-код:**

```python
from django.urls import reverse

print(reverse('post', args=(11,)))
# /post/11/
```

Результат указан для случая, когда этот маршрут подключён в корне сайта без дополнительного префикса.

**В шаблоне:**

```django
{% for p in posts %}
    <a href="{% url 'post' p.id %}">{{ p.title }}</a>
{% endfor %}
```

Или с именованным параметром:

```django
<a href="{% url 'post' post_id=p.id %}">{{ p.title }}</a>
```

Если заменить `post/<int:post_id>/` на `articles/<int:post_id>/`, но сохранить `name='post'`, ссылки, построенные через `{% url %}` и `reverse()`, автоматически начнут вести на `/articles/11/`. Менять все шаблоны не понадобится.

## I. 11. Тег `querystring`

`{% url %}` формирует **путь по имени маршрута**, а `{% querystring %}` изменяет **строку GET-параметров** после `?`, сохраняя остальные текущие параметры. Тег появился в Django 5.1.

Пусть адрес страницы:

```text
http://127.0.0.1:8000/?author=1&page=1
```

Тогда:

```django
{% querystring page=2 %}
```

сформирует:

```text
?author=1&page=2
```

А:

```django
{% querystring page=None %}
```

сформирует:

```text
?author=1
```

Полученная строка начинается с `?`, поэтому её можно непосредственно использовать в `href`: браузер оставляет текущий путь страницы и заменяет параметры запроса.

**Навигация:**

```django
<nav>
    <a href="{% querystring page=1 %}">Страница 1</a>
    <a href="{% querystring page=2 %}">Страница 2</a>
    <a href="{% querystring page=3 %}">Страница 3</a>
</nav>
```

Для автоматического доступа к текущему запросу нужен контекстный процессор:

```python
'django.template.context_processors.request'
```

Если `request` не добавляется в контекст автоматически, его можно передать вручную либо передать `QueryDict` тегу явно.

## I. 12. Наследование шаблонов

Повторение одной и той же разметки на разных страницах нарушает принцип **DRY (Don't Repeat Yourself)** — «не повторяйся». Наследование позволяет вынести общую структуру (шапку, меню, подвал) в базовый шаблон, а дочерним страницам оставить только отличающиеся части.

**Типичная структура:**

```text
project/
├── templates/
│   └── base.html
└── women/
    └── templates/
        └── women/
            └── about.html
```

Если `base.html` находится в общем каталоге проекта, его путь нужно включить в `DIRS`:

```python
'DIRS': [BASE_DIR / 'templates']
```

**`templates/base.html`:**

```django
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Сайт{% endblock %}</title>
</head>
<body>
    <header><h1>Мой сайт</h1></header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>Подвал сайта</footer>
</body>
</html>
```

**`women/about.html`:**

```django
{% extends 'base.html' %}

{% block title %}О сайте{% endblock %}

{% block content %}
    <h2>О проекте</h2>
    <p>Это страница с информацией о сайте.</p>
{% endblock %}
```

`extends` определяет родительский шаблон, а `block` — именованные участки, которые дочерний шаблон может переопределить. Блоков может быть несколько: `title`, `content`, `sidebar`, `styles`, `scripts` и другие.

## I. 13. Тег `include`: `with` и `only`

`include` вставляет результат отображения одного шаблона внутрь другого. Это удобно для повторяемых компонентов: меню, карточек, форм, панелей навигации.

**`women/nav.html`:**

```django
<nav>
    {% for item in menu %}
        <a href="{{ item.url }}">{{ item.title }}</a>
    {% endfor %}
</nav>
```

**`women/index.html`:**

```django
<!DOCTYPE html>
<html lang="ru">
<body>
    <header>
        {% include 'women/nav.html' %}
    </header>

    <main><h1>Главная страница</h1></main>

    <footer>
        {% include 'women/nav.html' with menu=footer_menu only %}
    </footer>
</body>
</html>
```

**Контекст представления:**

```python
data = {
    'menu': [
        {'title': 'Главная', 'url': '/'},
        {'title': 'Новости', 'url': '/news/'},
    ],
    'footer_menu': [
        {'title': 'Контакты', 'url': '/contacts/'},
    ],
}
```

В первом `include` фрагмент получает текущий контекст, включая `menu`. Во втором `with menu=footer_menu` явно передаёт переменную, а `only` запрещает доступ к остальному контексту родительского шаблона.

**Отличие от `extends`:** `include` вставляет повторно используемый фрагмент, а `extends` создаёт отношения «базовый шаблон — дочерняя страница» с переопределяемыми блоками.

## I. 14. Статические файлы

К статическим ресурсам относятся CSS, JavaScript, изображения и шрифты. Для них используется `django.contrib.staticfiles`.

**Структура:**

```text
women/
└── static/
    └── women/
        └── css/
            └── styles.css
```

В шаблоне загружают библиотеку `static`, чтобы создавать URL ресурсов:

```django
{% load static %}

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="{% static 'women/css/styles.css' %}">
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

При `STATIC_URL = 'static/'` типичный адрес ресурса:

```text
/static/women/css/styles.css
```

`{% load static %}` подключает библиотеку шаблонных тегов; сам CSS-файл он не читает.

При `DEBUG=True` стандартный `runserver` обслуживает статику в режиме разработки. При `DEBUG=False` это поведение отключается. Для **локальной проверки**, но не для production, можно запустить:

```bash
python manage.py runserver --insecure
```

Команда:

```bash
python manage.py collectstatic
```

собирает статические файлы приложений и дополнительных каталогов в `STATIC_ROOT` для последующей раздачи веб-сервером, CDN или middleware (например, WhiteNoise).

Дополнительный подкаталог `static/women` предотвращает конфликты одинаково названных файлов из разных приложений — по той же причине, что и `templates/women`.

## I. 15. Пользовательские шаблонные теги

В Django используются три способа регистрации пользовательских тегов:

1. `simple_tag` — вызов функции с возвращаемым результатом;
2. `inclusion_tag` — функция возвращает контекст для отдельного шаблона;
3. `simple_block_tag` — блочный тег с содержимым между открывающей и закрывающей конструкциями (появился в Django 5.2).

**Структура приложения:**

```text
women/
├── models.py
└── templatetags/
    ├── __init__.py
    └── women_tags.py
```

В `women_tags.py`:

```python
from django import template
from django.utils.safestring import mark_safe
from women.models import Category

register = template.Library()
```

`register = template.Library()` создаёт объект, с помощью которого Django регистрирует собственные теги и фильтры. После добавления нового модуля тегов следует перезапустить сервер разработки.

**Простой тег — список категорий:**

```python
@register.simple_tag
def get_categories():
    return Category.objects.all()
```

**Шаблон:**

```django
{% load women_tags %}
{% get_categories as categories %}

{% for cat in categories %}
    <p>{{ cat.name }}</p>
{% endfor %}
```

`as categories` сохраняет результат тега в переменной шаблона.

**Включающий тег с выбранной категорией:**

```python
@register.inclusion_tag('women/list_categories.html')
def show_categories(cat_selected=None):
    return {
        'categories': Category.objects.all(),
        'cat_selected': cat_selected,
    }
```

**`women/list_categories.html`:**

```django
<ul>
    {% for cat in categories %}
        <li>
            {% if cat.pk == cat_selected %}
                <strong>{{ cat.name }}</strong>
            {% else %}
                {{ cat.name }}
            {% endif %}
        </li>
    {% endfor %}
</ul>
```

**Вызов:**

```django
{% show_categories cat_selected=2 %}
```

**Блочный тег:**

```python
@register.simple_block_tag
def highlight(content):
    return mark_safe(f'<div class="highlight">{content}</div>')
```

**Использование:**

```django
{% highlight %}
    <p>Важный текст: {{ title }}</p>
{% endhighlight %}
```

Закрывающий тег имеет имя `end` + имя открывающего тега. Блочная функция получает уже отрендеренное внутреннее содержимое параметром `content`.

`mark_safe()` позволяет отдать результат как HTML, чтобы `<div>` не был экранирован. **Но `mark_safe()` не очищает HTML от вредоносного кода!** Его допустимо использовать только для гарантированно безопасных значений. Для интерполяции недоверенных строк в HTML лучше применять `format_html()`.

---

# Часть II. Базы данных и ORM Django

## II. 1. Основы ORM

**ORM (Object-Relational Mapping)** — объектно-реляционное отображение: классы Python соотносятся с таблицами БД, поля классов — со столбцами таблиц, экземпляры классов — с отдельными строками. Django переводит операции над моделями в SQL-запросы, соответствующие выбранной СУБД.

```python
from django.db import models


class Women(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
```

```python
Women.objects.create(
    title='Первая статья',
    content='Содержимое статьи',
)
```

Упрощённый смысл SQL:

```sql
INSERT INTO women_women (title, content)
VALUES ('Первая статья', 'Содержимое статьи');
```

В стандартной поставке Django поддерживает **SQLite, PostgreSQL, MySQL, MariaDB (через MySQL backend) и Oracle**.

**Преимущества ORM:** переносимость большей части кода между СУБД, удобные связи между объектами, параметризация запросов (защита от многих SQL-инъекций), работа с миграциями, меньше ручного SQL и интеграция с формами, админкой и представлениями. При оптимизации производительности знание SQL всё равно необходимо.

**`settings.py` для SQLite:**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

SQLite — стандартный вариант нового проекта Django; её база хранится в одном файле.

## II. 2. Поля модели: `id`, `pk`, даты, `blank`, `max_length`

Если первичный ключ не задан явно, Django автоматически добавляет `id`. Его тип по умолчанию обычно `BigAutoField` (в зависимости от `DEFAULT_AUTO_FIELD`). Атрибут `pk` — универсальное обращение к первичному ключу **независимо от его имени**. При стандартном ключе `obj.pk == obj.id`.

- `auto_now_add=True` — время при **создании** записи, после чего автоматически не меняется.
- `auto_now=True` — время при каждом стандартном сохранении `save()` (не при `QuerySet.update()`).
- `blank=True` — поле разрешается оставлять пустым при валидации форм; это **не** то же самое, что `null=True` в базе.

**Полный пример модели `Women`:**

```python
from django.db import models


class Women(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
```

Даты задаёт Django при сохранении модели. Для правильной работы часовых поясов в `settings.py` используются:

```python
USE_TZ = True
TIME_ZONE = 'Europe/Moscow'
```

При `USE_TZ=True` Django работает с aware-datetime. Для PostgreSQL время обычно приводится к UTC при хранении, а на уровне приложения отображается в требуемом часовом поясе. SQLite не хранит данные о часовом поясе непосредственно в типе datetime, поэтому соответствующие преобразования выполняет Django. При `USE_TZ=False` используются наивные datetime.

**`max_length` для `CharField` в Django 5.2:** стал необязателен для SQLite и ранее мог отсутствовать в PostgreSQL; для MySQL/MariaDB и Oracle его по-прежнему требуется указывать. Для переносимости кода разумно всегда задавать `max_length`.

## II. 3. Новшества Django 5.0–5.2

К заметным новшествам относятся:

- В **Django 5.0** появились `db_default` и `GeneratedField`.
- В **Django 5.2** появился `CompositePrimaryKey`.
- В **Django 5.2** `CharField` на SQLite стал поддерживать отсутствие `max_length`.

### `default` и `db_default`

`default` задаётся на уровне Python/Django, а `db_default` определяет значение по умолчанию **на уровне СУБД**, в том числе для внешних SQL-вставок, не использующих ORM.

```python
from django.db import models
from django.db.models.functions import Now


class Article(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(db_default=Now())
    status = models.IntegerField(db_default=0)
```

Если указать одновременно `default` и `db_default`, при создании объекта ORM приоритет имеет `default`.

### `GeneratedField`

`GeneratedField` — вычисляемый столбец, значение которого создаёт база данных:

- `expression` — SQL-выражение для расчёта;
- `output_field` — тип результата;
- `db_persist=True` — физически хранимое вычисляемое значение, `False` — виртуальное (возможности зависят от СУБД).

**Площадь квадрата:**

```python
from django.db import models
from django.db.models import F


class Square(models.Model):
    side = models.PositiveIntegerField()
    area = models.GeneratedField(
        expression=F('side') * F('side'),
        output_field=models.BigIntegerField(),
        db_persist=True,
    )

square = Square.objects.create(side=5)
square.refresh_from_db()
print(square.area)  # 25
```

### `CompositePrimaryKey`

Позволяет определить составной первичный ключ из нескольких полей:

```python
class OrderItem(models.Model):
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    pk = models.CompositePrimaryKey('order_id', 'product_id')
    quantity = models.PositiveIntegerField(default=1)
```

Уникальность записи определяется парой `(order_id, product_id)`. У составных ключей в Django 5.2 есть ограничения поддержки в отдельных компонентах, поэтому их используют там, где это действительно нужно.

## II. 4. Миграции и добавление уникального `slug`

**Миграция** — Python-файл с операциями изменения схемы базы данных. Django хранит миграции каждого приложения в каталоге `migrations` и отслеживает выполненные миграции в самой БД. Поэтому миграции можно считать контролем версий **структуры БД** (это не система контроля содержимого таблиц).

```text
women/
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    └── 0002_women_slug.py
```

Команды:

```bash
python manage.py makemigrations            # Создать файлы миграций
python manage.py sqlmigrate women 0001     # Посмотреть SQL миграции
python manage.py migrate                   # Применить миграции
```

`makemigrations` повторно запускают после изменений в определениях моделей, влияющих на схему: новых/удалённых полей, ограничений, индексов, части параметров `Meta` и прочего.

**Почему нельзя просто добавить `slug = SlugField(unique=True)` в заполненную таблицу?** Существующие записи не имеют слагов. Если для всех строк будет предложено одно и то же значение, ограничение `UNIQUE` нарушится; обязательное поле без подходящего значения тоже нельзя добавить без переходного этапа.

**Безопасная последовательность:**

**1. Добавляем временно необязательное поле:**

```python
slug = models.SlugField(
    max_length=255,
    null=True,
    blank=True,
)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

**2. Создаём отдельную миграцию данных:**

```bash
python manage.py makemigrations women --empty
```

В файл миграции:

```python
from django.db import migrations
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Women = apps.get_model('women', 'Women')

    for post in Women.objects.all().iterator():
        base = slugify(post.title, allow_unicode=True)[:200] or 'post'
        post.slug = f'{base}-{post.pk}'
        post.save(update_fields=['slug'])


class Migration(migrations.Migration):
    dependencies = [
        ('women', '0002_women_slug'),  # Заменить на реальную предыдущую миграцию
    ]

    operations = [
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
    ]
```

В этом учебном примере суффикс `-{post.pk}` обеспечивает уникальность создаваемых значений. Если используются Unicode-слаги, стандартный конвертер Django `<slug:...>` для них не подходит: следует использовать строковый или пользовательский конвертер. Для стандартного `<slug:...>` лучше формировать ASCII-слаги.

```bash
python manage.py migrate
```

**3. После заполнения делаем поле обязательным и уникальным:**

```python
slug = models.SlugField(max_length=255, unique=True)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

Для действующего проекта следует также продумать автоматическое заполнение слага при создании **новых** записей.

## II. 5. Создание записей и ленивость

Выражение:

```python
w = Women(title='Статья', content='Текст', slug='statya')
```

создаёт **объект Python**, но не строку в БД. Сохранение происходит при `w.save()`. Это отдельно от **ленивости QuerySet**: QuerySet обычно откладывает `SELECT` до момента, когда результаты реально потребуются.

**Способ 1 — конструктор и `save()`:**

```python
w = Women(
    title='Первая статья',
    content='Текст первой статьи',
    slug='first-post',
)
w.save()
```

**Способ 2 — `objects.create()`:**

```python
w = Women.objects.create(
    title='Вторая статья',
    content='Текст второй статьи',
    slug='second-post',
)
```

`create()` создаёт и сохраняет экземпляр сразу (по смыслу близко к сохранению с `force_insert=True`).

**Способ 3 — массовый `bulk_create()`:**

```python
Women.objects.bulk_create([
    Women(title='Третья статья', slug='third-post'),
    Women(title='Четвёртая статья', slug='fourth-post'),
])
```

В отличие от обычного `save()`, `bulk_create()` не вызывает его для каждого объекта и не отправляет обычные сигналы сохранения.

**Просмотр выполненных SQL-запросов:**

```python
from django.db import connection

Women.objects.create(title='Пятая статья', slug='fifth-post')

for query in connection.queries:
    print(query['sql'], query['time'])
```

Каждый элемент `connection.queries` содержит ключи `sql` (текст запроса) и `time` (время выполнения как строка). При стандартных настройках сбор истории запросов включён с `DEBUG=True`; иначе список может быть пустым.

## II. 6. Изменение и удаление записей

### Изменение экземпляра

```python
w = Women.objects.get(pk=1)
w.title = 'Новое название'
w.save()
```

**Упрощённый SQL:**

```sql
UPDATE women_women
SET title = 'Новое название'
WHERE id = 1;
```

При обычном `save()` Django может отправить в `UPDATE` и остальные поля, включая `time_update`. Чтобы явно ограничить набор изменяемых полей:

```python
w.save(update_fields=['title'])
```

### Массовое обновление

```python
Women.objects.filter(pk__lte=4).update(is_published=True)
```

SQL по смыслу:

```sql
UPDATE women_women
SET is_published = 1
WHERE id <= 4;
```

`update()` — метод **QuerySet**, который обновляет записи непосредственно SQL-запросом, не вызывая `save()` для каждого экземпляра.

**Почему нельзя `Women.objects.all()[:4].update(...)`?** Срез QuerySet соответствует ограничению результата через `LIMIT`/`OFFSET`. Django запрещает `update()` после среза, поскольку переносимая между поддерживаемыми СУБД массовая операция `UPDATE` над таким ограниченным набором не определена стандартным способом.

**Почему нельзя `Women.objects.get(pk=1).update(...)`?** `get()` возвращает *экземпляр модели*, а у экземпляров нет метода `update()`. Правильно:

```python
Women.objects.filter(pk=1).update(title='Новое название')
```

### Удаление

```python
Women.objects.filter(pk__in=[5, 6]).delete()
```

Пример SQL:

```sql
DELETE FROM women_women
WHERE id IN (5, 6);
```

Или удалить отдельный экземпляр:

```python
w = Women.objects.get(pk=5)
w.delete()
```

## II. 7. `filter()` и `get()`

`filter()` возвращает **QuerySet**, содержащий 0, 1 или много объектов. При отсутствии совпадений это **пустой QuerySet**, а не исключение.

`get()` возвращает **один объект модели**, а при нарушении этого требования вызывает исключение.

| Ситуация | `filter()` | `get()` |
|---|---|---|
| Найдена одна запись | QuerySet из одной записи | Объект модели |
| Найдено несколько | QuerySet из нескольких записей | `MultipleObjectsReturned` |
| Нет совпадений | Пустой QuerySet | `DoesNotExist` |

**Поиск по первичному ключу:**

```python
posts = Women.objects.filter(pk=3)  # QuerySet
post = Women.objects.get(pk=3)     # Women
```

`get()` особенно удобен там, где запись обязана быть единственной: поиск по первичному ключу или другому уникальному полю.

**Обработка отсутствующей записи:**

```python
try:
    post = Women.objects.get(pk=3)
    print(post.title)
except Women.DoesNotExist:
    print('Статья не найдена')
```

Для HTML-представлений, где отсутствие записи следует показать как HTTP 404, удобнее `get_object_or_404()`.

## II. 8. Fields lookups

**Field lookups** — суффиксы после двойного подчёркивания в условиях QuerySet, представляющие сравнения и другие операции SQL:

```python
Model.objects.filter(field__lookup=value)
```

Написать `filter(pk > 2)` нельзя: здесь нет именованного аргумента ORM, а выражение `pk > 2` само по себе не обращается к полю модели. Нужно передать условие через именованный аргумент, например `pk__gt=2`.

| Lookup | SQL-аналог | Значение |
|---|---|---|
| `exact` | `=` | Точное совпадение |
| `gt` | `>` | Больше |
| `gte` | `>=` | Больше или равно |
| `lt` | `<` | Меньше |
| `lte` | `<=` | Меньше или равно |
| `contains` | `LIKE '%...%'` | Подстрока |
| `icontains` | Сравнение без учёта регистра, зависит от СУБД | Подстрока без учёта регистра |
| `in` | `IN (...)` | Значение из множества |
| `isnull` | `IS NULL` / `IS NOT NULL` | Проверка NULL |

```python
Women.objects.filter(pk__gte=2)
# WHERE id >= 2

Women.objects.filter(title__contains='ли')
# WHERE title LIKE '%ли%' (упрощённо)
```

**`contains` и `icontains`:** второй вариант задаёт регистронезависимый поиск. Особенность SQLite: встроенный механизм `LIKE` в основном учитывает регистр лишь для ASCII, поэтому поиск по русским буквам может вести себя не так, как ожидается. В SQLite даже `contains` часто регистронезависим для латиницы, а `icontains` не обеспечивает корректное Unicode-сопоставление русских прописных/строчных букв без дополнительных механизмов.

**Несколько условий `AND`:**

```python
posts = Women.objects.filter(
    pk__in=[2, 5, 11, 12],
    is_published=True,
)
```

Упрощённый SQL:

```sql
SELECT * FROM women_women
WHERE id IN (2, 5, 11, 12)
  AND is_published = 1;
```

**Поиск по фрагменту названия:**

```python
posts = Women.objects.filter(title__contains='ли')
```

Для `OR` используется специальный класс **`Q`**:

```python
from django.db.models import Q

posts = Women.objects.filter(
    Q(title__icontains='ли') | Q(title__icontains='ма')
)
```

У объектов `Q` оператор `|` соответствует `OR`, `&` — `AND`, `~` — `NOT`.

## II. 9. `order_by()`: сортировка и индексы

`order_by()` добавляет сортировку по одному или нескольким полям в SQL-запрос.

**По возрастанию:**

```python
Women.objects.order_by('title')
# ORDER BY title ASC
```

**По убыванию:**

```python
Women.objects.order_by('-title')
# ORDER BY title DESC
```

Знак `-` перед именем поля означает `DESC`. Сортировка по нескольким полям:

```python
Women.objects.order_by('-time_create', 'title')
```

Методы ORM можно строить в цепочки, потому что операции вроде `filter()` и `order_by()` возвращают новые QuerySet:

```python
posts = (
    Women.objects
    .filter(is_published=True)
    .order_by('-time_create')
)
```

По умолчанию обычный QuerySet ленив и не выполняет `SELECT` до обращения к данным.

**Сортировка по умолчанию и индекс через `Meta`:**

```python
from django.db import models


class Women(models.Model):
    title = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(
                fields=['time_create'],
                name='women_created_idx',
            ),
        ]
```

`ordering` определяет обычный порядок выборки, а индекс `Index` может ускорять фильтрацию и сортировку по полю. Индексы имеют цену: место на диске и дополнительные операции при изменениях таблицы.

## II. 10. Слаги, `get_object_or_404()` и 404

**Slug** — человекочитаемый идентификатор записи в URL. Вместо `/post/11/` можно использовать `/post/django-template-guide/`: такой адрес легче понять и запомнить; он может помогать структуре сайта и SEO.

```python
slug = models.SlugField(
    max_length=255,
    unique=True,
    db_index=True,
)
```

- `unique=True` запрещает дублирующиеся слаги.
- `db_index=True` создаёт индекс для поиска (для `SlugField` индекс уже включён по умолчанию, а `unique=True` обычно также обеспечивает индекс — явное дублирование необязательно).

**`urls.py`:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('post/<slug:post_slug>/', views.show_post, name='post'),
]
```

**Представление:**

```python
from django.shortcuts import render, get_object_or_404
from .models import Women


def show_post(request, post_slug):
    post = get_object_or_404(Women, slug=post_slug)
    return render(request, 'women/post.html', {'post': post})
```

Если объект найден, он передаётся в контекст; иначе возникает `Http404` и формируется ответ 404.

**Эквивалент через `try/except`:**

```python
from django.http import Http404


def show_post(request, post_slug):
    try:
        post = Women.objects.get(slug=post_slug)
    except Women.DoesNotExist:
        raise Http404('Статья не найдена')
    return render(request, 'women/post.html', {'post': post})
```

При `DEBUG=False` Django показывает стандартную страницу 404 или настроенный шаблон `404.html`, а не подробную страницу отладки. `get_object_or_404()` не перехватывает `MultipleObjectsReturned`, если найдено несколько записей.

## II. 11. Метод `get_absolute_url()`

`get_absolute_url()` определяет URL конкретного объекта модели. Обычно он возвращает **абсолютный путь от корня сайта**, а не полный URL с доменом. Внутри метода удобно применять `reverse()` по имени маршрута.

**Модель статьи:**

```python
from django.db import models
from django.urls import reverse


class Women(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})
```

Маршрут:

```python
path('post/<slug:post_slug>/', views.show_post, name='post')
```

**Модель категории:**

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})
```

Маршрут:

```python
path('category/<slug:cat_slug>/', views.show_category, name='category')
```

**Список рубрик в шаблоне:**

```django
<ul>
    {% for cat in categories %}
        <li>
            <a href="{{ cat.get_absolute_url }}">{{ cat.name }}</a>
        </li>
    {% endfor %}
</ul>
```

В шаблоне **не нужны скобки** у `cat.get_absolute_url`: движок Django автоматически вызывает методы объектов без обязательных аргументов при разрешении переменных.

**Два преимущества перед непосредственным `{% url %}` в каждой ссылке:**

1. Логика построения URL централизована в модели и не повторяется в шаблонах.
2. Метод доступен не только в шаблонах, но и в Python-коде, админке и других компонентах приложения.

Тег `{% url %}` удобен для общих маршрутов (главная, логин, контакты) и адресов, которые не являются каноническими ссылками на конкретный объект.

## II. 12. Собственные менеджеры и `IntegerChoices`

Менеджер предоставляет API для получения объектов модели. Стандартное имя — `objects`.

**Менеджер только опубликованных статей:**

```python
from django.db import models


class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
```

`get_queryset()` формирует исходный QuerySet для операций менеджера. Переопределение позволяет применять общий фильтр автоматически.

```python
class Women(models.Model):
    title = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)

    objects = models.Manager()
    published = PublishedModel()
```

```python
Women.objects.all()    # Все статьи
Women.published.all()  # Только опубликованные
```

Если объявить только собственный менеджер `published`, Django не создаст стандартный `objects` автоматически. Для сохранения обоих имён нужно явно указать `objects = models.Manager()`.

### Перечисление `IntegerChoices`

`IntegerChoices` хранит коды статусов числами и предоставляет человекочитаемые подписи.

**Полный пример после перехода от логического поля к перечислению:**

```python
from django.db import models


class PublishedModel(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=Women.Status.PUBLISHED
        )


class Women(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255)

    is_published = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT,
    )

    objects = models.Manager()
    published = PublishedModel()

    def __str__(self):
        return self.title
```

Свойства перечисления:

```python
Women.Status.choices
# [(0, 'Черновик'), (1, 'Опубликовано')]

Women.Status.values
# [0, 1]

Women.Status.labels
# ['Черновик', 'Опубликовано']
```

`choices` используются в формах, административном интерфейсе и механизмах валидации значений. Для вывода подписи статуса объекта можно вызвать:

```python
post.get_is_published_display()  # 'Черновик' или 'Опубликовано'
```

После перехода на перечисление фильтр менеджера вместо булева `True` сравнивает статус с `Women.Status.PUBLISHED`.

## II. 13. `ForeignKey` и правила `on_delete`

`ForeignKey` задаёт отношение **многие к одному**: каждая статья принадлежит одной категории, а категория может содержать много статей. В этом примере `Category` — **первичная (родительская)** модель, а `Women` — **вторичная (зависимая)**.

У `ForeignKey` два обязательных аргумента:

1. `to` — целевая модель (можно указать строкой `'Category'`).
2. `on_delete` — действие при удалении связанной родительской записи.

Указание модели строкой позволяет сослаться на класс, объявленный позже, и избегать некоторых циклических импортов.

**Вариант CASCADE:**

```python
cat = models.ForeignKey(
    'Category',
    on_delete=models.CASCADE,
)
```

**Вариант PROTECT:**

```python
cat = models.ForeignKey(
    'Category',
    on_delete=models.PROTECT,
)
```

### Значения `on_delete`

| Значение | Последствия при удалении родительской записи |
|---|---|
| `CASCADE` | Удаляются также все связанные зависимые записи |
| `PROTECT` | Удаление запрещается с `ProtectedError` |
| `SET_NULL` | Внешний ключ записей становится `NULL`; требуется `null=True` |
| `SET_DEFAULT` | Связь заменяется значением `default` (должна быть корректная связанная запись) |
| `SET(value)` или `SET(callable)` | Устанавливается переданное значение или результат вызова функции |
| `DO_NOTHING` | Django не меняет зависимые записи; при ограничениях целостности БД возможен `IntegrityError` |

Дополнительно в Django есть `RESTRICT`: удаление ограничивается через `RestrictedError`, но в некоторых случаях допускается при совместном каскадном удалении связанных объектов.

Если категория используется статьями, **`PROTECT` запрещает её удаление**, а **`CASCADE` удаляет категорию вместе со связанными статьями**.

### Добавление обязательного ключа в заполненную таблицу

При добавлении нового внешнего ключа старые статьи ещё не имеют категорий. Чтобы не нарушить ограничение `NOT NULL`, выполняют последовательность:

**1. Временное nullable-поле:**

```python
cat = models.ForeignKey(
    'Category',
    on_delete=models.PROTECT,
    null=True,
    blank=True,
)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

**2. Назначение категории старым записям:**

```python
from women.models import Women, Category

default_category, created = Category.objects.get_or_create(
    name='Без категории',
    defaults={'slug': 'uncategorized'},
)

Women.objects.filter(cat__isnull=True).update(cat=default_category)
```

Для командного проекта и повторяемых развёртываний заполнение данных лучше оформить миграцией `RunPython`, а не выполнять только через консоль.

**3. Удаление возможности NULL:**

```python
cat = models.ForeignKey('Category', on_delete=models.PROTECT)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

Теперь у каждой статьи обязательно должна быть категория.

## II. 14. Связи many-to-one, `cat_id`, `cat`, обратная выборка

Рассмотрим поле:

```python
cat = models.ForeignKey('Category', on_delete=models.PROTECT)
```

```python
w = Women.objects.get(pk=1)
print(w.cat_id)  # ID категории, дополнительный SELECT не нужен
print(w.cat)     # Объект Category
```

`w.cat_id` берёт идентификатор из уже загруженного поля модели; **нового SQL-запроса нет**.

`w.cat` обращается к связанному объекту. При первом обращении, если объект не был заранее загружен, Django выполняет **один дополнительный SQL-запрос**. Затем объект обычно кэшируется в экземпляре `w`.

Чтобы уменьшить количество SQL-запросов, используют `select_related()`:

```python
w = Women.objects.select_related('cat').get(pk=1)
print(w.cat.name)  # Обычно без отдельного SELECT
```

### Обратная связь

При отсутствии `related_name` Django создаёт обратное имя вида `<имя_модели>_set`:

```python
cat = Category.objects.get(pk=1)
posts = cat.women_set.all()
```

Его можно переименовать:

```python
cat = models.ForeignKey(
    'Category',
    on_delete=models.PROTECT,
    related_name='posts',
)
```

Теперь:

```python
cat = Category.objects.get(pk=1)
posts = cat.posts.all()
```

### Фильтрация через связанные поля

**По списку ID категорий:**

```python
Women.objects.filter(cat__in=[1, 2, 5])
Women.objects.filter(cat_id__in=[1, 2, 5])
```

**По слагу категории:**

```python
Women.objects.filter(cat__slug='sport')
```

**По фрагменту названия категории:**

```python
Women.objects.filter(cat__name__contains='Спорт')
```

**Все категории со статьями, в заголовках которых есть «ли»:**

```python
categories = (
    Category.objects
    .filter(posts__title__contains='ли')
    .distinct()
)
```

В примере предполагается, что для `Women.cat` установлен `related_name='posts'`.

**Зачем `distinct()`?** При SQL-соединении таблиц категория может попасть в результат несколько раз, если несколько её статей соответствуют условию. `distinct()` устраняет дубликаты категорий посредством `SELECT DISTINCT`.

## II. 15. `ManyToManyField` и `OneToOneField`

### Многие ко многим (`ManyToManyField`)

Один пост может иметь несколько тегов, и один тег может относиться к нескольким постам. В отличие от `ForeignKey`, для связи **многие ко многим** обычно создаётся отдельная промежуточная таблица:

```text
women_women
-----------
id
title

women_tagpost
-------------
id
tag

women_women_tags
----------------
id
women_id
tagpost_id
```

Для `ManyToManyField` не задают параметр `on_delete`: удаление строк связи управляется промежуточной таблицей и механизмами Django. При удалении поста или тега обычно удаляются соответствующие строки связи, но не другие посты или теги.

**Модель тегов `TagPost`:**

```python
from django.db import models


class TagPost(models.Model):
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag
```

**Поле `tags` у модели `Women`:**

```python
class Women(models.Model):
    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(
        TagPost,
        blank=True,
        related_name='posts',
    )
```

**Создание и связывание объектов:**

```python
post = Women.objects.create(title='Новая статья')
tag1 = TagPost.objects.create(tag='Python')
tag2 = TagPost.objects.create(tag='Django')

post.tags.add(tag1, tag2)  # Добавить обе связи
post.tags.set([tag1])     # Заменить набор связей
post.tags.remove(tag1)    # Удалить конкретную связь
post.tags.clear()         # Удалить все связи
```

`remove()` и `clear()` удаляют отношения, но **не сами записи `TagPost`**.

Нельзя передать `tags=[tag1, tag2]` в `Women.objects.create(...)`, поскольку many-to-many связи нельзя назначить как обычные поля при таком создании объекта. Сначала модель сохраняют, чтобы появился первичный ключ; затем используют `add()` или `set()`.

### Один к одному (`OneToOneField`)

Связь **один к одному** обеспечивает уникальность связи: один объект `Husband` не может одновременно быть назначен нескольким записям `Women`.

**Модель `Husband`:**

```python
class Husband(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```

**Модель с полем `husband`:**

```python
class Women(models.Model):
    title = models.CharField(max_length=255)
    husband = models.OneToOneField(
        Husband,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wuman',
    )
```

`SET_NULL` означает, что при удалении мужа соответствующее поле `Women.husband` станет `NULL`. `related_name='wuman'` задаёт имя обратного доступа к связанной записи.

**Назначение связи:**

```python
h = Husband.objects.create(name='Александр')
w = Women.objects.create(title='Первая запись')

w.husband = h
w.save()

print(h.wuman)  # Связанная запись Women
```

Сохранять изменение связи нужно **в модели `Women`**, потому что именно в её таблице расположен внешний ключ `husband_id`. Объект `Husband` должен уже существовать в базе.

**Попытка назначить того же мужа второй записи:**

```python
w2 = Women.objects.create(title='Вторая запись')
w2.husband = h
w2.save()  # IntegrityError: нарушена уникальность
```

Чтобы переназначить связь, нужно сначала освободить её у предыдущей записи. Удобно выполнить обе операции атомарно:

```python
from django.db import transaction

with transaction.atomic():
    w.husband = None
    w.save(update_fields=['husband'])

    w2.husband = h
    w2.save(update_fields=['husband'])
```

Если по смыслу задачи одному `Husband` разрешено соответствовать нескольким записям `Women`, вместо `OneToOneField` необходимо использовать `ForeignKey`.

---

## Краткий итог

В документе разобраны **все 30 вопросов** контрольной работы № 2: 15 о шаблонах Django и 15 об ORM, моделях, миграциях и связях в базе данных. Для большинства вопросов приведено несколько примеров; код ориентирован на объяснение изучаемого механизма, а не на единый полностью настроенный проект.
