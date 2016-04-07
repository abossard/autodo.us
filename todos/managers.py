
from django.db import models
from django.db.models.aggregates import Sum, Count
         
class BookManager( models.Manager):
    def get_queryset(self):
        return super(BookManager, self).get_queryset().annotate(
            duration_a=Sum('task__line__duration'),
            count_a=Count('task')
        )

class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().annotate(
            duration_a=Sum('line__duration'),
            count_a=Count('line')
        )

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
        return self.by_book_id(book_id).filter(line__end__range=date_range)

    def by_book_id(self, book_id):
        return super(TaskManager, self).get_queryset().filter(book__id=book_id)


class TagManager(models.Manager):
    def get_queryset(self):
        return super(TagManager, self).get_queryset().annotate(
            duration_a=Sum('tagged__line__duration'),
            count_a=Count('tagged'),
        )

    def by_book_id(self, book_id):
        return super(TagManager, self).get_queryset().filter(tagged__book__id=book_id).annotate(duration=Sum('tagged__line__duration'))

class PersonManager(models.Manager):
    def get_queryset(self):
        return super(PersonManager, self).get_queryset().annotate(
            duration_a=Sum('sitsin__line__duration'),
            count_a=Count('sitsin')
        )

    def by_book_id(self, book_id):
        return super(PersonManager, self).get_queryset().filter(sitsin__book__id=book_id).annotate(duration=Sum('sitsin__line__duration'))


class LineManager(models.Manager):
    def today(self):
        return self.day(datetime.today())

    def yesterday(self):
        return self.day(datetime.today()-timedelta(1))
    
    def day(self, date):
        date_range = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return self.all().filter(end__range=date_range)