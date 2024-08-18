from django.db import models
import datetime 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, max_length=50, on_delete= models.CASCADE)
    date_modefied = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    old_cart = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
      return self.user.username
    
  # Create a CustomerProfile by defult when user sings up 
    @receiver(post_save, sender=User)
    def created_profile(sender, instance, created, **kwargs):
      if created:
         user_profile = CustomerProfile(user=instance)
         user_profile.save()
  

         
# Categories of Prodcuts
class Category(models.Model):
    name = models.CharField( max_length=50)
    
    def __str__(self):
        return self.name
    
    class Meta:
      verbose_name_plural = 'categories'

# Customers
class Customer(models.Model):
    first_name = models.CharField( max_length=50)
    last_name = models.CharField( max_length=50)
    phone = models.CharField( max_length=10)
    email = models.EmailField( max_length=254)
    password= models.CharField( max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" 
    

# All of our Product
class Product(models.Model):
    name = models.CharField( max_length=100) 
    price = models.DecimalField( max_digits=5, decimal_places=2 ,default=0)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=1 )
    description = models.TextField(max_length=1000, default='',blank=True)
    image = models.ImageField( upload_to='uploads/product/')
    # Add sales stuff
    is_sale = models.BooleanField(default=False) 
    sale_price = models.DecimalField( max_digits=5, decimal_places=2 ,default=0)
    
     

    def __str__(self):
        return self.name
    

# Customer Orders 
class Order(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    adress = models.CharField(max_length=200 ,default='', blank=True )
    phone = models.CharField( max_length=20,default='')
    data = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)



    def __str__(self):
      return self.product

    
