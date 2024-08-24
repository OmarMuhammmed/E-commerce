from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from store.models import Product
from django.db.models.signals import post_save,pre_save
import datetime


class ShippingAdderss(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    address1 = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)

    # Create a Shipping Profile by defult when user sings up 
    @receiver(post_save, sender=User)
    def created_shipping_adderss(sender, instance, created, **kwargs):
      if created:
         user_shipping = ShippingAdderss(user=instance)
         user_shipping.save()

    class Meta:
      verbose_name_plural = 'Shipping Adderss'

    def __str__(self):
      return f'Shipping Adderss - {str(self.id)}'
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_adderss = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)	
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    # paypal data
    invoice = models.CharField(max_length=250, blank=True, null=True)
    paid = models.BooleanField(default=False)
    

    def __str__(self):
      return f'Order - {str(self.id)}'

# Auto add shipping date before save any Order
@receiver(pre_save, sender = Order)
def auto_shipped_date(sender, instance, **kwargs):
    if instance.pk:
       now = datetime.datetime.now()
       obj = sender._default_manager.get(pk=instance.pk)
       if instance.shipped and not obj.shipped:
          instance.date_shipped = now

    


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField( max_digits=5, decimal_places=2)
    
    def __str__(self):
      return f'OrderI tem - {str(self.id)}'
    






    



  

   