from django.urls import path, include
from . import views
from rest_framework_nested import routers


router =routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products-detail')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)

# pprint(router.urls)
# urlpatterns = [
#     # path('products/', views.ProductList.as_view()),
#     # path('products/<int:pk>/', views.ProductDetail.as_view()),
#     # # path('collections/<int:pk>/', views.collection_detail, name='collection-detail'),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>/', views.CollectionDetail.as_view())
# ]

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(carts_router.urls))

]