from django.apps import AppConfig


class TodosConfig(AppConfig):
    name = 'todos'
    verbose_name = "To do or not to do"
    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Task'))
