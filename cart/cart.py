from store.models import Product,CustomerProfile
from payment.models import Coupon
from decimal import Decimal


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.request = request
        # Get cart from session 
        cart = self.session.get('cart')  
        # create a cart when not exisits {} 
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

    def save(self):
        ''' Mark the session as modified to save changes to the cart '''
        self.session.modified = True 

    def manage_cart(self) :
        """ Each user has his own cart especially."""
        # Deal with login user 
        if self.request.user.is_authenticated:
            current_user = CustomerProfile.objects.filter(user__id= self.request.user.id ) 
            # Convert {'3':1, '2':4} to {"3":1, "2":4} B Json not error
            carty = str(self.cart)
            carty = carty.replace("\'", "\"") # \ To ignore error
            # Save carty to the CustomerProfile Model
            current_user.update(old_cart=str(carty))
      

    def db_add(self, product, quantity):
        product_id = str(product) 
        product_qty = int(quantity)
        
        if product_id in self.cart:
            self.cart[product_id] += product_qty  
        else: 
            self.cart[product_id] = product_qty  
        
        self.save()
        self.manage_cart()
     
     
    def add(self, product, quantity):
        # Convert product ID to string to use as a key in the cart dictionary
        product_id = str(product.id) 
        # Convert the quantity to an integer
        product_qty = int(quantity)
        
        if product_id in self.cart:
            self.cart[product_id] += product_qty  
        else: 
            self.cart[product_id] = product_qty  
        
        self.save()
        self.manage_cart()
     

    def __len__(self):
        return len(self.cart)
    
    def get_products(self):
        # get ids from Cart
        products_id = self.cart.keys()
        # use ids to search in DB model (Product)
        products = Product.objects.filter(id__in=products_id)
        return products
    
    def get_qty_for_product(self):
        return self.cart  

    def update(self, product, quantity):
        product_id = str(product.id)  
        product_qty = int(quantity)
        mycart = self.cart
        mycart[product_id] = product_qty  
       
        self.manage_cart()
        self.save()
        return self.cart

	 
    def delete(self, product):
        product_id = str(product.id) 
        if product_id in self.cart:
            del self.cart[product_id]

        self.save()
        self.manage_cart()



    def total(self):
        total = 0 
        products = self.get_products()
        for product in products:
            quantity = self.cart.get(str(product.id), 0)  # 0 is Defult value 
            if product.is_sale:
                total += product.sale_price * quantity
            else:
                total += product.price * quantity
        return Decimal(total) 
    
    @property
    def coupon(self):
        if self.coupon_id:
            try :
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass

           
    @property
    def get_discount(self):
        if self.coupon:
             return (self.total() * Decimal(self.coupon.discount) / Decimal(100))
        return Decimal(0)
    # get discount Percentage 
    @property
    def get_discount_percentage(self):
        if self.coupon:
            return self.coupon.discount  
        return 0

    @property
    def get_total_price_after_discount(self):

        return Decimal(self.total() - self.get_discount + Decimal(10)) # 10 is shipping price