import graphene
from graphene import relay, resolve_only_args
from graphene.contrib.django import DjangoNode, DjangoObjectType

from todos.models import Book, Task, Tag, Person, Line
from graphene.core.classtypes.objecttype import ObjectType
from graphene.contrib.django.filter.fields import DjangoFilterConnectionField

class BookNode(DjangoNode):

    class Meta:
        model = Book
        filter_fields = ['name', 'is_open']
        filter_order_by = ['name', 'is_open']

    @classmethod
    def get_node(cls, id, info):
        return BookNode(Book.objects.get(id))


class TaskNode(DjangoNode):

    class Meta:
        model = Task
        filter_fields = ['text', 'finished', 'active', 'updated']
        filter_order_by = ['text', 'finished', 'active', 'updated']

    @classmethod
    def get_node(cls, id, info=None):
        return TaskNode(Task.objects.get(id))


class Query(ObjectType):
    book = relay.NodeField(BookNode)
    all_books = DjangoFilterConnectionField(BookNode)

    task = relay.NodeField(TaskNode)
    all_tasks = DjangoFilterConnectionField(TaskNode)

    class Meta:
        abstract = True
