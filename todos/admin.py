from django.contrib import admin
from todos.models import Book, Task, Tag, Person, Line
from reversion.admin import VersionAdmin


@admin.register(Task)
class TaskAdmin(VersionAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    pass
