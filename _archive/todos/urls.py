from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('autodous.todos.views',
                       (r'edittask/(?P<task_id>\d+)$', 'edittask'),
                       (r'editline/(?P<line_id>\d+)$', 'editline'),
                       (r'start_work/(?P<task_id>\d+)$', 'start_work'),
                       (r'stop_work/(?P<task_id>\d+)$', 'stop_work'),
                       (r'stop_work/(?P<task_id>\d+)/(?P<finished>[01])/$', 'stop_work'),
                       (r'taskbook/$', 'taskbook'),
                       (r'^book/(?P<book_id>\d+)/add/?$', 'addtask'),
                       (r'^book/add/?$', 'addbook'), 
                       (r'^book/(?P<book_id>\d+)/?$', 'workbook'),
                       (r'^book/?$', 'workbook'),
                       (r'^/?$', 'workbook'),
)
