import decimal
from rest_framework import serializers
from store.models import Product, CartItem, Collection, Review, Cart, Customer, Order, OrderItem
from decimal import Decimal
from django.db import transaction

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
    # collection = CollectionSerializer()
    
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length = 255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source= 'unit_price')
    # collection = serializers.PrimaryKeyRelatedField(queryset= Collection.objects.all())
    # collection = serializers.StringRelatedField()


    def calculate_tax( self, product:Product):
        return product.unit_price * Decimal(1.1)


class CartItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = CartItem    
        fields = ['id', 'product', 'quantity', 'total_price'] 
    product = ProductSerializer()  
    total_price = serializers.SerializerMethodField(method_name = 'get_total_price')
    def get_total_price (self, cart_item:CartItem):
        return  cart_item.quantity * cart_item.product.unit_price  

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField() 
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity'] 
        
    def validate_product_id(self, value): #the function name here is a standard naming conention: It must be explicitly written as validate_<field name in serializer class>
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with this Id exist!!!')
        return value
    
    def save(self,**kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity'] 
        cart_id = self.context['cart_id']
        
        # print(product_id)
    
        try:
            
            existing_cart_item = CartItem.objects.get(cart_id= cart_id, product_id= product_id)
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
            self.instance = existing_cart_item
            
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data) 
        
        return self.instance
    
class UpdateCartItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = CartItemSerializer
        fields = ['quantity']

    

class CartSerializer (serializers.ModelSerializer):
    id = serializers.UUIDField(read_only= True)
    cartitem_set = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price (self, cart:Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.cartitem_set.all() ])
    class Meta:
        model = Cart
        fields = ['id', 'cartitem_set', 'total_price']

class CustomerSerializer (serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only = True)
    class Meta:
        model = Customer
        fields = ['id', 'phone', 'birth_date', 'membership', 'user_id']

class OrderItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'unit_price', 'quantity', 'product']
    product = ProductSerializer()  
        
class OrderSerializer (serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)  
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'orderitem_set']
        
class  CreateOrderSerializer (serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id (self, cart_id):
        cart_exist = Cart.objects.filter(pk = cart_id).exists()
        if not cart_exist:
            raise serializers.ValidationError('No Cart with the given ID exists')
        if CartItem.objects.filter(pk=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is Empty')
        return cart_id

    def save (self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            (customerId, created) = Customer.objects.only('id').get_or_create(user_id = self.context['user_id'] )
            
            #Operation 1: SAVE A ORDER RECORD (IMO, I wouldn't do this shaa, I would combine the order item and order tablle together nii)
            order = Order.objects.create(customer = customerId) #Here I can equally say .create(customer_id = customerId.id) because the customerId, in realityy, returns the customer object and not really an Id
            
            #Operation 2: GET THE CART ITEMS CORRESPONDNG TO THE CART ID 
            cart_items = CartItem.objects \
                                .select_related('product') \
                                .filter(cart_id = cart_id)
            
            #Operation 3: COPY ALL THE FETCHED CART ITEMS INTO THE ORDER ITEM TABLE 
            order_items = [
                OrderItem(
                    order_id = order.id,
                    product_id = item.product.id,
                    quantity = item.quantity,
                    unit_price = item.product.unit_price
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            
            #Operation 4: DELETE THE CART (Since we use moodel.CASCADE, all order items attached will be deleted too)
            Cart.objects.filter(pk=cart_id).delete()
            
            return order
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
        
        
        
        
        