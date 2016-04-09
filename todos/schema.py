import graphene
from graphene import relay, resolve_only_args
from graphene.contrib.django import DjangoNode, DjangoObjectType

from todos.models import Book, Task, Tag, Person, Line
from graphene.core.classtypes.objecttype import ObjectType
from graphene.contrib.django.filter.fields import DjangoFilterConnectionField
from graphene import Scalar

from django.utils.dateparse import (
    parse_date, parse_datetime, parse_duration, parse_time,
)

class Timedelta(Scalar):
    '''Duration'''
    
    @staticmethod
    def serialize(timedelta):
        return str(timedelta)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return parse_duration(node.value)

    @staticmethod
    def parse_value(value):
        return parse_duration(value)

class BookNode(DjangoNode):
    duration = Timedelta()
    
    class Meta:
        model = Book
        filter_fields = ['name', 'is_open']
        filter_order_by = ['name', 'is_open']

class TaskNode(DjangoNode):
    duration = Timedelta()
    class Meta:
        model = Task
        filter_fields = ['text', 'finished', 'active', 'updated']
        filter_order_by = ['text', 'finished', 'active', 'updated']

class TagNode(DjangoNode):
    duration = Timedelta()
    class Meta:
        model = Tag
        filter_fields = ['name']
        filter_order_by = ['name']

class PersonNode(DjangoNode):
    duration = Timedelta()
    class Meta:
        model = Person
        filter_fields = ['name']
        filter_order_by = ['name']
        
class Query(ObjectType):
    book = relay.NodeField(BookNode)
    all_books = DjangoFilterConnectionField(BookNode)

    task = relay.NodeField(TaskNode)
    all_tasks = DjangoFilterConnectionField(TaskNode)
    
    tag = relay.NodeField(TagNode)
    all_tags = DjangoFilterConnectionField(TagNode)
    
    person = relay.NodeField(PersonNode)
    all_persons = DjangoFilterConnectionField(PersonNode)

    class Meta:
        abstract = True
