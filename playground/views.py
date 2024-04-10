from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer, Order, Collection
from django.db.models import Value, F, Func, Count
from django.db.models.functions import Concat

# Create your views here.

def hello_world(request):
    # queryset = Customer.objects.annotate(
    #     full_name = Concat(F('first_name'),Value(' ') ,F('last_name'))
    # )

    # grouping data

    # queryset = Customer.objects.annotate(
    #     orders_count = Count('order')
    # )
    # create record
    # collection = Collection(id=11)
    # collection.title = 'Games'
    # collection.featured_product = None
    # collection.save()

    # update specific one record
    Collection.objects.filter(id=11).update(featured_product_id=2)
    context = {
        'name': 'Allen',
        # 'result': list(queryset)
    }
    
    return render(request, 'hello.html',context)