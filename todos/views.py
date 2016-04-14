import logging as log
from datetime import datetime, time

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response as base_render_to_response
from django.template import RequestContext
from django.contrib import messages

from .models import Book, Task, Person, Tag, Line
from .forms import BookForm, TaskForm, LineForm


def render_to_response(request, template, context):
    return base_render_to_response(template, context, context_instance=RequestContext(request))

# Create your views here.


@login_required
def workbook(request, book_id=None):
    books = Book.objects.filter(owner=request.user)
    if book_id:
        current_book = Book.objects.get(owner=request.user, id=int(book_id))
    else:
        if books:
            current_book = books[0]
        else:
            current_book = None
        #current_book = Book.objects.filter(owner=request.user)[1]
    newtask = TaskForm()
    newbook = BookForm()
    active_tasks = Task.objects.active()
    finished_tasks = Task.objects.finished_by_book_id(book_id)
    open_tasks = Task.objects.open_by_book_id(book_id)
    tags = Tag.objects.by_book_id(book_id)
    persons = Person.objects.by_book_id(book_id)
    todays_work = Task.objects.today_by_book_id(book_id)
    yesterdays_work = Task.objects.yesterday_by_book_id(book_id)
    return render_to_response(request, 'workbook.html', {
        'books': books,
        'current_book': current_book,
        'active_tasks': active_tasks,
        'newtask': newtask,
        'newbook': newbook,
        'media': newtask.media,
        'tags': tags,
        'persons': persons,
        'todays_work': todays_work,
        'yesterdays_work': yesterdays_work,
        'finished_tasks': finished_tasks,
        'open_tasks': open_tasks,
    })


def taskbook(request):
    tasks = Task.objects.filter(book__owner=request.user).select_related('book__owner').extra(
        select={
            'time_spent': 'SELECT SUM(duration)/60 FROM todos_line WHERE todos_line.task_id=todos_task.id'},
        # select_params=('a',)
    )
    people = Person.objects.filter(sitsin__person=request.user).select_related(
        'sitsin__person').distinct()
    tags = Tag.objects.filter(tagged__person=request.user).select_related(
        'tagged', 'tagged_person').distinct()
    return render_to_response(request, 'tasks.html', {
        'tasks': tasks,
        'people': people,
        'tags': tags,
    })


def addtask(request, book_id=None):
    log.debug("in add task")
    if request.method == 'POST' and book_id:
        newtask = TaskForm(request.POST, instance=Task(book_id=book_id))
        if newtask.is_valid():
            task = newtask.save()
            messages.info(request, "Task %s created" % task)
            return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': book_id}))
        else:
            log.info("addtask: form not valid")
    else:
        log.info("addtask: no book_id")
    return HttpResponseRedirect(reverse(workbook))


def addbook(request):
    if request.method == 'POST':
        newbook = BookForm(request.POST, instance=Book(owner=request.user))
        if newbook.is_valid():
            the_book = newbook.save()
            messages.info(request, "New book %s created" % the_book)
            return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': the_book.id}))
    return HttpResponseRedirect(reverse(workbook))


def edittask(request, task_id=None):
    try:
        task = Task.objects.get(id=int(task_id))
        lines = task.line_set.exclude(start=None).reverse()
    except Task.DoesNotExist:  # @UndefinedVariable
        log.warn("task with id %s does not exist" % (task_id,))
        return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': task.book.id}))

    if request.method == 'POST':
        editform = TaskForm(request.POST, instance=task)
        if editform.is_valid():
            editform.save()
            log.debug("task %s successfully saved" % (task,))
            messages.info(request, "task edited")
            return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': task.book.id}))
    else:
        editform = TaskForm(instance=task)
    return render_to_response(request, 'edittask.html', {'editform': editform, 'task': task, 'lines': lines})


def editline(request, line_id=None):
    try:
        line = Line.objects.get(id=int(line_id))
    except Line.DoesNotExist:  # @UndefinedVariable
        log.warn("line with id %s does not exist" % (line_id,))
        return HttpResponseRedirect(reverse(edittask, kwargs={'task_id': line.task.id}))
    if request.method == 'POST':
        editform = LineForm(request.POST, instance=line)
        if editform.is_valid():
            editform.save()
            messages.info(request, "line edited")
            log.debug("line %s successfully saved" % (line,))
            return HttpResponseRedirect(reverse(edittask, kwargs={'task_id': line.task.id}))
    else:
        editform = LineForm(instance=line)
    return render_to_response(request, 'editline.html', {'editform': editform, 'line': line})


def start_work(request, task_id=None):
    task = Task.objects.get(id=int(task_id))
    task.active = True
    task.save()
    messages.info(request, "work started on %s" % task)
    return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': task.book.id}))


def stop_work(request, task_id=None, finished=None):
    task = Task.objects.get(id=int(task_id))
    task.active = False
    task.finished = True if finished else False
    task.save()
    messages.info(request, "work stopped on %s" % task)
    return HttpResponseRedirect(reverse(workbook, kwargs={'book_id': task.book.id}))
