from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'edittask/(?P<task_id>\d+)$', views.edittask),
    url(r'editline/(?P<line_id>\d+)$', views.editline),
    url(r'start_work/(?P<task_id>\d+)$', views.start_work),
    url(r'stop_work/(?P<task_id>\d+)$', views.stop_work),
    url(r'stop_work/(?P<task_id>\d+)/(?P<finished>[01])/$', views.stop_work),
    url(r'taskbook/$', views.taskbook),
    url(r'book/(?P<book_id>\d+)/add$', views.addtask),
    url(r'book/add$', views.addbook),
    url(r'book/(?P<book_id>\d+)$', views.workbook),
    url(r'book$', views.workbook),
    url(r'^$', views.workbook),
]
