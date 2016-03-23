import re
import logging as log
from datetime import datetime, timedelta, time
from time import mktime

from django.db import models
from django.db import connection, transaction
from django.db.models import Sum, Count
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from autodous.todos.fields import TimedeltaField

class Book(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User)
    
    class Meta:
        ordering=('name', )
        unique_together = ('name','owner')
    def __unicode__(self):
        return self.name

class TaskManager(models.Manager):
    def active(self):
        return self.filter(active=True)

    def finished_by_book_id(self, book_id):
        return self.filter(book__id=book_id, finished=True)

    def open_by_book_id(self, book_id):
        return self.filter(book__id=book_id, finished=False)

    def today_by_book_id(self, book_id):
        return self.date_by_book_id(datetime.today(), book_id)

    def yesterday_by_book_id(self, book_id):
        return self.date_by_book_id(datetime.today()-timedelta(1), book_id)

    def date_by_book_id(self, date, book_id):
        date_range = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return self.by_book_id(book_id).filter(line__end__range=date_range).annotate(duration=Sum('line__duration'))

    def by_book_id(self, book_id):
        return super(TaskManager, self).get_query_set().filter(book__id=book_id)
    
    def get_query_set(self):
        return super(TaskManager, self).get_query_set().annotate(duration=Sum('line__duration'))

class Task(models.Model):
    text = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    book = models.ForeignKey(Book)
    active = models.BooleanField(default=False)
    duration = TimedeltaField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    current_line = models.ForeignKey('Line', related_name='current_task', blank=True, null=True, default=None) # we blanked it, because the signal fills it out

    objects = TaskManager()
   
    class Meta:
        ordering = ('-finished', 'created',)
        unique_together = ('text','book')
    class Admin:
        list_filter = ('text', 'owner', 'finished',)
    def __unicode__(self):
        return self.text

def task_line_management(sender, **kwargs):
    task = kwargs['instance']
    try:
        line = task.current_line
        if task.active:
            #can happen only once per line
            print "task.active!"
            if not line.start:
                print "set line start"
                line.start = datetime.now()
                line.save()
            else:
                log.warn("line already started (ignore in fixtures)") 
        #task not active here           
        elif line and line.start and not line.end:
            # finish up work
            # arriving here menas: Task is not active, and has a current_line that has not set an end
            # we'll set an end and create a new line.
            line.end = datetime.now()
            line.passed_on = True
            line.save()
            #now we finished and check if we should create a new line
            if not task.finished:
                newline = Line(task=task, book=task.book)
                newline.save()
                task.current_line = newline
                task.save()
            else:
                task.current_line = None
                task.save()
    except Line.DoesNotExist:
        log.warn( "no current line on task: %s (ignore in fixtures)"%(task,))

def task_line_init(sender, **kwargs):
    task = kwargs['instance']
    print "task_line_init: ", task
    try:
        if not task.current_line:
            if kwargs['created']:
                newline = Line(task=task, book=task.book)
                newline.save()
                print "create init line: ", newline  
                task.current_line=newline
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
class TagManager(models.Manager):

    def by_book_id(self, book_id):
        return super(TagManager, self).get_query_set().filter(tagged__book__id=book_id).annotate(duration=Sum('tagged__line__duration'))

    def get_query_set(self):
        return super(TagManager, self).get_query_set().annotate(duration=Sum('tagged__line__duration'))
    
class Tag(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    tagged = models.ManyToManyField(Task)
    duration = TimedeltaField(default=0)

    objects = TagManager()

    class Meta:
        ordering = ()
    
    def time_spent(self):
        if True:
            return 10
        duration = timedelta(0)
        for task in self.tagged.all():
            duration += task.time_spent()
        return duration

    def __unicode__(self):
        return "#%s" % (self.name,)

class PersonManager(models.Manager):

    def by_book_id(self, book_id):
        return super(PersonManager, self).get_query_set().filter(sitsin__book__id=book_id).annotate(duration=Sum('sitsin__line__duration'))

    def get_query_set(self):
        return super(PersonManager, self).get_query_set().annotate(duration=Sum('sitsin__line__duration'))


class Person(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    sitsin = models.ManyToManyField(Task)
    duration = TimedeltaField(default=0)
    
    objects = PersonManager()
    
    def time_spent(self):
        if True:
            return 10
        duration = timedelta(0)
        for task in self.sitsin.all():
            #print task.time_spent()
            duration += task.time_spent()
        return duration
    
    def __unicode__(self):
        return "@%s" % (self.name,)

class LineManager(models.Manager):

    def today(self):
        return self.day(datetime.today())

    def yesterday(self):
        return self.day(datetime.today()-timedelta(1))
    
    def day(self, date):
        date_range = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return self.all().filter(end__range=date_range)


class Line(models.Model):
    task =  models.ForeignKey(Task)
    passed_on = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    book = models.ForeignKey(Book)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    duration = TimedeltaField(default=0)

    objects = LineManager()

    class Meta:
        ordering = ('-created',)
    def __unicode__(self):
        if self.start and self.end and self.duration:
            return "%s for %s" %(self.start.strftime('%H:%M'),self.duration,)
        elif self.start:
            return "%s in work" %(self.start.strftime('%H:%M'),)
        else:
            return "empty"

def duration_aggregation(sender, **kwargs):
    line = kwargs['instance']
    # first we update the line
    if line.start and line.end:
        line.duration = line.end - line.start
        log.debug('set duration to %s'%(line.duration,))
        
    #now we update the duration field of the task
##    task_id = line.task.id
##    log.debug("aggregating for task_id",task_id)
##    cursor = connection.cursor()
##    sql =          """  UPDATE todos_task
##                        SET "duration" = (
##                            SELECT SUM("duration")
##                            FROM todos_line
##                            WHERE "task_id" = %(task_id)s)
##                        WHERE id=%(task_id)s
##                    """ % { 'task_id':task_id, }
    #cursor.execute(sql)
    #transaction.commit_unless_managed()
        

pre_save.connect(duration_aggregation, sender=Line)

##def pre_save_work_aggregation(sender, **kwargs):
##    work = kwargs['instance']
##    if work.end:
##        work.duration = work.end - work.start
##        print work.duration
##pre_save.connect(pre_save_work_aggregation, sender=Work)
##
##def post_save_work_aggregation(sender, **kwargs):
##    work = kwargs['instance']
##    #lets update the duration with a custom sql. Just because we can ....
##    task_id = work.task.id
##    cursor = connection.cursor()
##    #cursor.execute("UPDATE todos_task SET todos_task.duration = (SELECT SUM("duration") from todos_work WHERE "task_id" = %s) WHERE id = %s", [task_id, task_id])
##    cursor.execute('UPDATE todos_task SET "duration" = (SELECT SUM("duration") from todos_work WHERE "task_id" = %s) WHERE "id" = %s', [task_id,task_id,])
##    #print "UPDATE todos_tasks SET todos_tasks.duration = (SELECT SUM(todos_work.duration) from todos_work WHERE todos_work.task_id = %s) WHERE id = %s"%( task_id, task_id)
##    transaction.commit_unless_managed()
##    print "UPDATEDDD!!!"
##    
##post_save.connect(post_save_work_aggregation, sender=Work)
