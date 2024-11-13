from django.contrib import admin
from .models import ShippingAdderss, OrderItem, Order, Coupon
from django.contrib.auth.models import User

admin.site.register(ShippingAdderss)
admin.site.register(Order)
admin.site.register(OrderItem)
  
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0 
    

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ['date_ordered']
    fields = ['user','full_name','email','shipping_adderss','amount_paid','date_ordered','shipped','date_shipped','invoice','paid']
    inlines = [OrderItemInline]
    
admin.site.unregister(Order)
admin.site.register(Order, OrderAdmin)

@admin.register(Coupon)

class CouponAdmin(admin.ModelAdmin):

    list_display = ['code', 'valid_from', 'valid_to',

                    'discount', 'active']

    list_filter = ['active', 'valid_from', 'valid_to']

    search_fields = ['code']