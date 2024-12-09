from django.http import HttpResponse
from django.http import HttpRequest


def home(request):
    return HttpResponse("Welcome to App")