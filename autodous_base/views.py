from django.http.response import HttpResponse

def home(request):
    return HttpResponse("Hello, world. You're at the polls index.")
