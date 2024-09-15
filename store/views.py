from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import  Collection, Product, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

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


