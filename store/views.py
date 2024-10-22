from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Collection, Product, Order, OrderItem, Review, Cart, CartItem, Customer
from .serializers import (CollectionSerializer,UpdateCartItemSerializer, CartItemSerializer, 
                          AddCartItemSerializer, ProductSerializer, ReviewSerializer, CartSerializer, 
                          CustomerSerializer, OrderSerializer, OrderItemSerializer, CreateOrderSerializer, UpdateOrderSerializer)
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .permissions import isAdminOrReadOnly, ViewCustomerHistoryPermission
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from django.db.models import Count

# Create your views here.

class ReviewViewSet (ModelViewSet):
   # queryset = Review.objects.all()
   serializer_class = ReviewSerializer

   def get_queryset(self):
      return Review.objects.filter(product_id = self.kwargs['product_pk'])

   def get_serializer_context(self):
      return {'product_id': self.kwargs['product_pk']}
   
   

class ProductViewSet (ModelViewSet):
   queryset = Product.objects.all()
   serializer_class = ProductSerializer
   filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
   pagination_class= PageNumberPagination
   filterset_fields = ['collection_id']
   search_fields = ['title', 'description']
   ordering_fields = ['unit_price', 'last_update']
   permission_classes = [isAdminOrReadOnly]
   # We can also use filter_class in place of filter_fields for generic filter , such as filtering less than or greater than a value 

   # def get_queryset(self):
   #    queryset = Product.objects.all()
   #    collection_id = self.request.query_params.get('collection_id')

   #    if collection_id is not None:
   #       queryset = queryset.filter(collection_id= collection_id)

   #    return queryset

   def get_serializer_context(self):
      return {'request': self.request}
   
   def delete (self, request, pk):
      product = get_object_or_404(Product, pk=pk)
      if product.orderitems.count() > 0:
         return Response({'error':'Product cannot be deleted'})
      product.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet (ModelViewSet):
   queryset = Cart.objects.prefetch_related('cartitem_set__product').all()
   serializer_class = CartSerializer
   
      
class CartItemViewSet (ModelViewSet):
   # serializer_class = CartItemSerializer
   def get_serializer_class(self):
      if self.request.method == 'POST':
         return AddCartItemSerializer
      elif self.request=='PATCH':
         return UpdateCartItemSerializer
      return CartItemSerializer
   
   def get_serializer_context(self):
      return {'cart_id': self.kwargs['cart_pk']}  
     
   def get_queryset(self):
      # print(self.kwargs['cart_pk'])
      return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])

   
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    #This function is an alternative to the permission_classes atttribute defined above, especially if you want to explicitly set permission on each request methods
    #As a result, this function overrides the above attribute (permission_classes)
   #  def get_permissions(self):
   #    if self.request.method == "GET":
   #       return [AllowAny()]
   #    return [IsAuthenticated()]
    
    @action(detail= True, permission_classes=[ViewCustomerHistoryPermission])
    def history (self, request, pk):
      return Response('OKayyyyed')
       
    @action(detail=False, methods = ['GET', 'PUT'], permission_classes=[IsAuthenticated]) #permission_class parameter can also be added here
    def profile(self, request):
      (customer, created) = Customer.objects.get_or_create(user_id = request.user.id) 
      if request.method == 'GET':
         serializer = CustomerSerializer(customer)
         return Response(serializer.data )
      elif request.method == 'PUT':
         serializer = CustomerSerializer(customer, data= request.data)
         serializer.is_valid(raise_exception = True)
         serializer.save()
         return Response(serializer.data)
        
         
class OrderViewSet(ModelViewSet):
   #  queryset = Order.objects.all()
   #  serializer_class = OrderSerializer
   #  permission_classes = [IsAuthenticated]
    
    def get_permissions (self):
       if self.request.method in ['PUT', 'PATCH', 'DELETE']:
          return [IsAdminUser()]
       return [IsAuthenticated()]
    
    def create (self, request):
       serializer = CreateOrderSerializer(
          data= request.data,
          context = {'user_id': self.request.user.id} #THIS IS THE SAME AS THE get_serializer_context method. We use this since we are over-riding the create method in the viewset
       )
       serializer.is_valid(raise_exception=True)
       order = serializer.save()
       serializer = OrderSerializer(order)
       return Response(serializer.data)
    
    
    def get_serializer_class (self):
       if self.request.method == 'POST':
          return CreateOrderSerializer
       elif self.request.method == 'PATCH':
          return UpdateOrderSerializer
       return OrderSerializer
    
   #THIS IS NOT NEEDED ANYMORE SINCE THE create METHOD HAS BEEN EXPLICITLY OVERRIDDEN, AND THE CONTEXT ARGUMENT HAS BEEN SUPPLIED TO THE serializer attribute in the create method 
   #  def get_serializer_context(self):
   #     return {'user_id': self.request.user.id}
    
    def  get_queryset(self):
      if self.request.user.is_staff:
         return Order.objects.all()
 
      (customerId, created) = Customer.objects.only('id').get_or_create(user_id = self.request.user.id)
      # print(customerId)
      return Order.objects.filter(customer_id = customerId)
       
    


  


#THIS IS A CLASS BASED VIEW 
class ProductList (APIView):
   def get (self, request):
      queryset = Product.objects.select_related('collection').all()
      # The select_related class is like the populate method in mongoose 
      serializer = ProductSerializer(queryset, many=True)
      return Response(serializer.data)
   
   def post (self, request):
      serializer = ProductSerializer(data= request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()

class ProductDetail (APIView):  
   def get (self, request, id):
      product = get_object_or_404(Product, pk=id)
      serializer = ProductSerializer(product)
      return Response(serializer.data)
   
   def put (self, request, id):
      product = get_object_or_404(Product, pk=id)
      serializer = ProductSerializer(product, data= request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data)
   
   def delete (self, request, id):
      product = get_object_or_404(Product, pk=id)
      if product.orderitem_set.count() > 0:
         return Response(status= status.HTTP_405_METHOD_NOT_ALLOWED)
      product.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)


# THIS IS A FUNCTION BASED VIEW 
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def collection_list (request):
   if request.method == 'GET':
      queryset = Collection.objects.annotate(n_products= Count('product')).all()

      serializer = CollectionSerializer(queryset, many=True)
     
      return Response(serializer.data)
   
   elif request.method == 'POST':
      serializer = CollectionSerializer(data = request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status= status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE']) 
def collection_details (request, id):
   if request.method == 'GET':
      collection = get_object_or_404(
         Collection.objects.annotate(n_products= Count('product'))  , 
         pk=id)
      serializer = CollectionSerializer(collection) 
      print('products', collection.product_set.count())
      # print('products', collection.Product)
      return Response(serializer.data)
   
   elif request.method == 'PUT':
      collection = get_object_or_404(Collection, pk=id)
      serializer = CollectionSerializer(collection, data= request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data)

   elif request.method == 'DELETE':
      collection = get_object_or_404(Collection, pk=id)
      collection.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)

      

# @api_view(['GET', 'POST'])
# def product_list(request):
#    if request.method == 'GET':
#         queryset = Product.objects.select_related('collection').all()
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data)
#    elif request.method == 'POST':
#         print('yee')
#         serializer = ProductSerializer(data= request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
     #    print(serializer.validated_data)
      #   return Response(serializer.data, status=status.HTTP_201_CREATED)
   
        # if serializer.is_valid():
        #     serializer.validated_data 
        #     return Response('OK')
        # else :
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail (request, id):
#    product = get_object_or_404(Product, pk=id)
#    if request.method == 'GET':    
#       serializer = ProductSerializer(product)
#       return Response(serializer.data)
#    elif request.method== "PUT":
#       serializer = ProductSerializer(product, data= request.data)
#       serializer.is_valid(raise_exception=True)
#       serializer.save()
#       return Response(serializer.data)
#    elif request.method == 'DELETE':
#       if product.orderitem_set.count() > 0:
#           return Response(status= status.HTTP_405_METHOD_NOT_ALLOWED)
#       product.delete()
#       return Response(status=status.HTTP_204_NO_CONTENT)

#    try:
#         product = Product.objects.get(pk = id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#    except Product.DoesNotExist:
#        return Response(status=status.HTTP_404_NOT_FOUND)


