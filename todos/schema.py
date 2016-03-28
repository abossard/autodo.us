import graphene
from graphene import relay, resolve_only_args
from graphene.contrib.django import DjangoNode, DjangoObjectType

from todos.models import Book, Task, Tag, Person, Line

schema = graphene.Schema(name='Autodo.us Schema')

def get_book(id):
    pass

class BookNode(DjangoNode):
    class Meta:
        model = Book

    @classmethod
    def get_node(cls, id, info):
        return BookNode(Book.objects.get(id))

class TaskNode(DjangoNode):
    class Meta:
        model= Task