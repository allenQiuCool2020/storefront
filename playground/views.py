from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, OrderItem, Order
from django.db.models import Q, F
from django.db.models.aggregates import Max, Min, Count, Avg
# Create your views here.

def hello_world(request):
    # queryset = Product.objects.filter(collection__id=3).order_by('unit_price')
    # queryset = OrderItem.objects.values('product_id').distinct()
    # queryset = Product.objects.prefetch_related('promotions').all()
    result = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))
    context = {
        'name': 'Allen',
        'result': result
    }
    
    return render(request, 'hello.html',context)