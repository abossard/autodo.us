from django.db import models

import re
import logging
from todos.managers import BookManager, TaskManager, TagManager, PersonManager, LineManager
from django.utils import timezone
import rules
from django.db.models.expressions import F
log = logging.getLogger(__name__)

from datetime import datetime, timedelta, time
from time import mktime

from django.db import models
from django.db import connection, transaction
from django.db.models import Sum, Count
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist


@rules.predicate
def is_book_owner(user, book):
    return book.owener == user

rules.add_rule('can_edit_book', is_book_owner)
rules.add_rule('can_delete_book', is_book_owner)


class DurationMixin:

    @property
    def duration(self):
        return self.duration_a

    def duration_orderable(self):
        return self.duration_a
    duration_orderable.admin_order_field = 'duration_a'


class CountMixin:
    
    @property
    def count(self):
        return self.count_a

    def count_orderable(self):
        return self.count_a
    count_orderable.admin_order_field = 'count_a'


class Book(CountMixin, DurationMixin, models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User)
    is_open = models.BooleanField(default=True)

    objects = BookManager()

    class Meta:
        ordering = ('name', )
        unique_together = ('name', 'owner')

    def __str__(self):
        return self.name


class Task(CountMixin, DurationMixin, models.Model):
    text = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    book = models.ForeignKey(Book)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_line = models.ForeignKey(
        'Line',
        related_name='current_task',
        blank=True,
        null=True,
        default=None)  # we blanked it, because the signal fills it out

    objects = TaskManager()

    class Meta:
        ordering = ('-finished', 'created',)
        unique_together = ('text', 'book')

    class Admin:
        list_filter = ('text', 'owner', 'finished',)

    def __str__(self):
        return self.text


def task_line_management(sender, **kwargs):
    task = kwargs['instance']
    try:
        line = task.current_line
        if task.active:
            # can happen only once per line
            log.info("task.active!")
            if not line.start:
                log.info("set line start")
                line.start = timezone.now()
                line.save()
            else:
                log.warn("line already started (ignore in fixtures)")
        # task not active here
        elif line and line.start and not line.end:
            # finish up work
            # arriving here menas: Task is not active, and has a current_line that has not set an end
            # we'll set an end and create a new line.
            line.end = timezone.now()
            line.passed_on = True
            line.save()
            # now we finished and check if we should create a new line
            if not task.finished:
                newline = Line(task=task, book=task.book)
                newline.save()
                task.current_line = newline
                task.save()
            else:
                task.current_line = None
                task.save()
    except Line.DoesNotExist:
        log.warn("no current line on task: %s (ignore in fixtures)" % (task,))


def task_line_init(sender, **kwargs):
    task = kwargs['instance']
    log.info("task_line_init: ", task)
    try:
        if not task.current_line:
            if kwargs['created']:
                newline = Line(task=task, book=task.book)
                newline.save()
                log.info("create init line: ", newline)
                task.current_line = newline
                task.save()
    except Line.DoesNotExist:
        log.warn("not existing line assigned (ignore in fixtures)")

post_save.connect(task_line_init, sender=Task)
post_save.connect(task_line_management, sender=Task)


def tag_and_people_management(sender, **kwargs):
    task = kwargs['instance']
    task.tag_set.clear()
    for tag in re.findall('#(\w+)', task.text):
        dbtag, created = Tag.objects.get_or_create(name=tag)
        task.tag_set.add(dbtag)
    task.person_set.clear()
    for name in re.findall('@(\w+)', task.text):
        dbperson, created = Person.objects.get_or_create(name=name)
        task.person_set.add(dbperson)

post_save.connect(tag_and_people_management, sender=Task)


class Tag(CountMixin, DurationMixin, models.Model):
    name = models.SlugField(max_length=50)
    tagged = models.ManyToManyField(Task, related_name='tag_set')

    objects = TagManager()

    class Meta:
        ordering = ()

    def __str__(self):
        return "#%s" % (self.name,)


class Person(CountMixin, DurationMixin, models.Model):
    name = models.CharField(max_length=50)
    sitsin = models.ManyToManyField(Task)

    @property
    def duration(self):
        return self.duration_a

    objects = PersonManager()

    def __str__(self):
        return "@%s" % (self.name,)


class Line(models.Model):
    task = models.ForeignKey(Task)
    passed_on = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(Book)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    objects = LineManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        if self.start and self.end and self.duration:
            return "%s for %s" % (self.start.strftime('%H:%M'), self.duration,)
        elif self.start:
            return "%s in work" % (self.start.strftime('%H:%M'),)
        else:
            return "empty"


def duration_aggregation(sender, **kwargs):
    line = kwargs['instance']
    # first we update the line
    if line.start and line.end:
        line.duration = line.end - line.start
        log.debug('set duration to %s' % (line.duration,))

pre_save.connect(duration_aggregation, sender=Line)


# def duration_propagation(sender, **kwargs):
#    line = kwargs['instance']
#    base_task_qs = Task.objects.filter(id=line.task_id)
#    task = base_task_qs.annotate(d=Sum('line__duration'))[:1]
#    if task:
#        base_task_qs.update(duration=task[0].d)

#post_save.connect(duration_propagation, sender=Line)

# def post_save_work_aggregation(sender, **kwargs):
##    work = kwargs['instance']
# lets update the duration with a custom sql. Just because we can ....
##    task_id = work.task.id
##    cursor = connection.cursor()
# cursor.execute("UPDATE todos_task SET todos_task.duration = (SELECT SUM("duration") from todos_work WHERE "task_id" = %s) WHERE id = %s", [task_id, task_id])
##    cursor.execute('UPDATE todos_task SET "duration" = (SELECT SUM("duration") from todos_work WHERE "task_id" = %s) WHERE "id" = %s', [task_id,task_id,])
# print "UPDATE todos_tasks SET todos_tasks.duration = (SELECT SUM(todos_work.duration) from todos_work WHERE todos_work.task_id = %s) WHERE id = %s"%( task_id, task_id)
# transaction.commit_unless_managed()
# print "UPDATEDDD!!!"
##
##post_save.connect(post_save_work_aggregation, sender=Work)
