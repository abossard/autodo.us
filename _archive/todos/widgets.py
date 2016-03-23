from django import forms

class InPlaceTextInput(forms.TextInput):
    def __init__(self, attrs={}):
        attrs.update({'class': 'in_place'})
        super(InPlaceTextInput, self).__init__(attrs=attrs)
        

    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
            'http://cdn.jquerytools.org/1.0.2/jquery.tools.min.js',
            )
        
