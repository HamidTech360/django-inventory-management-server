from django.db import models

# Create your models here.

class Promotion (models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Collection (models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='+')

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update= models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion)

    def __str__(self) -> str:
        return self.title

class Customer(models.Model):
    MEMBERSHIP_CHOICES = [
        ('B', 'Bronze'),
        ('G', 'Gold'),
        ('S', 'Silver')
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default='B')
    # class Meta :
    #     db_table = 'store_customers'
    #     indexes = [models.Index(fields=['last_name', 'first_name'])]

class OrderItem (models.Model):
    order = models.ForeignKey('Order', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Order(models.Model):
    PAYMENT_STATUS = [
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=2, choices=PAYMENT_STATUS, default='P')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class Address (models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
   # customer = models.OneToOneField(Customer, on_delete=models.SET_CASCADE, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    zip = models.CharField(max_length=255, null=True)

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem (models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

class Review (models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    

