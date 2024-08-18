from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    product_qty = cart.get_qty_for_product()
    total = cart.total() 
    return render(request, 'cart_summary.html', {'cart_products': cart_products,
                                                  'product_qty': product_qty,
                                                    'total': total,
                                                    })

def cart_add(request):
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        # get product with id 
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        # add product to cart use add function 
        cart.add(product=product, quantity=product_qty)
        
        cart_quantity = cart.__len__() # length in frontend
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request,message="Product Added  To Cart ....")
        return response

def cart_update(request):
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        cart = Cart(request)
        cart.update(product=Product(id=product_id), quantity=product_qty) 
        messages.success(request,message=" Cart has been  Updated  ....") 
        response = JsonResponse({'qty': product_qty})
        return response


def cart_delete(request):
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart = Cart(request)
        cart.delete(product=Product(id=product_id))  
        response = JsonResponse({'product': product_id})
        messages.success(request,message=" Product Deleted From Cart  ....")
        return response
