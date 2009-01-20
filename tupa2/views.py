from django.http import HttpResponse
# coding: latin-1

def index(request):

    return HttpResponse("<html><p><A href='./admin/'>AdminSivu.</A><p><h1>Tähän tulee Tupan testisivustot...</h1><p></html>")

