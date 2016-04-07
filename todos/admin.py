from django.contrib import admin
from todos.models import Book, Task, Tag, Person, Line
from reversion.admin import VersionAdmin


@admin.register(Task)
class TaskAdmin(VersionAdmin):
    list_display = [
        'text',
        'description',
        'finished',
        'active',
        'created',
        'updated',
        'duration',
        'count'
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'owner',
        'is_open',
        'duration',
        'count'
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'duration',
        'count'
    ]


@admin.register(Person)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'duration',
        'count'
    ]

@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = [
        'created',
        'task',
        'start',
        'end',
        'duration'
    ]
