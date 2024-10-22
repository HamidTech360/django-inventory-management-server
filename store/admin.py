from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse 
from . import models


# Register your models here.

class InventoryFilter (admin.SimpleListFilter):
    title="inventory"
    parameter_name="inventory"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10', 'Low')
        ]
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == "<10":
            return queryset.filter(inventory__lt =10)

@admin.register(models.Collection)
class CollectionAdmin (admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields=['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({
            'collection__id': str(collection.id)
        })

        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request) :
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions=['clear_inventory']
    autocomplete_fields=['collection']
    # fields=['title', 'slug']
    exclude=['promotions']
    prepopulated_fields={
        'slug':['title']
    }

    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related= ['collection']
    list_filter=['collection', 'last_update', InventoryFilter]

    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        else:
            return 'OK'
    
    def collection_title (self, product):
        return product.collection.title
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset:QuerySet):
        updated_count = queryset.update(inventory = 0)
        self.message_user(request, f'{updated_count} products were succesfulled updatediii')



@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    search_fields=['first_name__istartswith']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    
    def orders_count(self, customer):
        url = reverse('admin:store_order_changelist') + '?' + urlencode({
            'customer__id':str(customer.id)
        })
         
        return format_html('<a href="{}">{}</a>',url, customer.orders_count)

 
    def get_queryset(self, request) :
        return super().get_queryset(request).annotate(
            orders_count = Count('order')
        )


@admin.register(models.Order)
class OrderAdmin (admin.ModelAdmin):
    list_display = ['payment_status','placed_at', 'customer_name']
    list_select_related = ['customer']

    def customer_name (self, order):
        return order.customer.first_name

#admin.site.register(models.Product)
