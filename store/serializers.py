import decimal
from rest_framework import serializers
from store.models import Product, Collection, Review
from decimal import Decimal

# class CollectionSerializer (serializers.Serializer):
    
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length = 255)

class ReviewSerializer (serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
        

class CollectionSerializer (serializers.ModelSerializer):
    class Meta: 
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.SerializerMethodField(method_name='get_products_count')
    # n_products = serializers.IntegerField()

    def get_products_count (self, collection):
        return collection.product_set.count()



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'slug', 'description', 'inventory', 'collection', 'price_with_tax']
        #fields = '__all__'

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = CollectionSerializer()
    
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source= 'unit_price')
    # collection = serializers.PrimaryKeyRelatedField(queryset= Collection.objects.all())
    # collection = serializers.StringRelatedField()


    def calculate_tax( self, product:Product):
        return product.unit_price * Decimal(1.1)