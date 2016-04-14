from django import forms
from django.forms.widgets import TextInput
from .models import Task, Book, Line

class TaskForm(forms.ModelForm):
    text = forms.CharField(widget=TextInput(attrs={'size':50}))
    class Meta:
        model = Task
        fields = ['text',]


class BookForm(forms.ModelForm):
    name = forms.CharField(widget=TextInput(attrs={'size':50}))
    class Meta:
        model = Book
        fields = ['name',]

class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        fields = ['start','end']

