from django.contrib import admin
from todos.models import Book, Task, Tag, Person, Line

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
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