from django.urls import path
from django.conf.urls import include
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('carts', views.CartViewSet)
router.register('products', views.ProductViewSet, basename='product')
router.register('customers', views.CustomerViewSet, basename= 'customer')
router.register('orders', views.OrderViewSet, basename='orders')
#The basename argument will be used behind the scene in constructing the name of the view classes/functions like so product-list/ product-details

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product') #the lookup argument will allegedly allow  the query param be represented as product_pk
products_router.register('reviews', views.ReviewViewSet, basename='product-review')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup="cart")
carts_router.register('items', views.CartItemViewSet, basename = 'cart-items')




urlpatterns = [
  
    # path('products', views.ProductList.as_view()),
    # path('products/<int:id>', views.ProductDetail.as_view()),
    path('collections', views.collection_list),
    path('collections/<int:id>', views.collection_details),

    #This kind of path definition, as opposed to the above, is used for viewset views (not class based views or functin based )
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(carts_router.urls))
]