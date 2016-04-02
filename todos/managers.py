
from django.db import models
from django.db.models.aggregates import Sum


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
        return super(TaskManager, self).get_queryset().filter(book__id=book_id)


class TagManager(models.Manager):

    def by_book_id(self, book_id):
        return super(TagManager, self).get_queryset().filter(tagged__book__id=book_id).annotate(duration=Sum('tagged__line__duration'))

    def get_queryset(self):
        return super(TagManager, self).get_queryset().annotate(duration=Sum('tagged__line__duration'))


class PersonManager(models.Manager):

    def by_book_id(self, book_id):
        return super(PersonManager, self).get_queryset().filter(sitsin__book__id=book_id).annotate(duration=Sum('sitsin__line__duration'))

    def get_queryset(self):
        return super(PersonManager, self).get_queryset().annotate(duration=Sum('sitsin__line__duration'))


class LineManager(models.Manager):

    def today(self):
        return self.day(datetime.today())

    def yesterday(self):
        return self.day(datetime.today()-timedelta(1))
    
    def day(self, date):
        date_range = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return self.all().filter(end__range=date_range)