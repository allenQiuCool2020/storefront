from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product
# Create your views here.

def hello_world(request):
    queryset = Product.objects.filter(title__icontains='coffee')
    context = {
        'name': 'Allen',
        'products': list(queryset)
    }
    
    return render(request, 'hello.html',context)