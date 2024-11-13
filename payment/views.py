from django.shortcuts import render
from .forms import ShippingInfoForm, PaymentForm, CouponForm
from cart.cart import Cart
from .models import ShippingAdderss, Order, OrderItem, Coupon
from django.shortcuts import redirect
from django.contrib import messages
from store.models import CustomerProfile, Product
import datetime
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.views.decorators.http import require_POST
from django.utils import timezone


def checkout(request):
    cart = Cart(request)
    now = timezone.now()
    cart_products = cart.get_products()
    product_qty = cart.get_qty_for_product()
    total = cart.total()
    shipping_price = 10 
    finally_price = shipping_price + total
    coupon_form = CouponForm()

    total_after_discount = None
    discount = None 

    # Cupon system 
    if request.method == 'POST' and 'coupon_code' in request.POST:
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            code = coupon_form.cleaned_data['coupon_code']
            try:
                coupon = Coupon.objects.get(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True
                )
                request.session['coupon_id'] = coupon.id
               
                total_after_discount = cart.get_total_price_after_discount
                discount = cart.get_discount
                discount_percentage = cart.get_discount_percentage
                messages.success(request, 'Coupon Applied')
                return render(request, 'payment/checkout.html', {
                    "cart_products": cart_products, 
                    "product_qty": product_qty, 
                    "total": total,
                    "total_after_discount": total_after_discount,
                    "discount": discount,
                    'coupon_form': coupon_form,
                    "shipping_price": shipping_price,
                    "discount" : discount,
                    'shipping_form': ShippingInfoForm(),
                    'discount_percentage': discount_percentage,
                })

            except Coupon.DoesNotExist:
                messages.error(request, 'This coupon is not valid')

        return redirect('checkout')
        
    


   
    if request.user.is_authenticated:
        shipping_user = ShippingAdderss.objects.get(user__id=request.user.id)
        shipping_form = ShippingInfoForm(request.POST or None, instance=shipping_user)
        
        return render(request, 'payment/checkout.html', {
            "cart_products": cart_products,
            "product_qty": product_qty,
            "total": total,
            "shipping_price":shipping_price,
            "finally_price": finally_price,
            "coupon_form": coupon_form,
            "total_after_discount": total_after_discount,
            "discount": discount,
            "shipping_form": shipping_form,
            'discount_percentage': discount_percentage,
        })
    
    else:
        shipping_form = ShippingInfoForm(request.POST)
        return render(request, 'payment/checkout.html', {
            'cart_products': cart_products,
            'product_qty': product_qty,
            'total': total,
            "shipping_price": shipping_price,
            'finally_price': finally_price,
            'shipping_form': shipping_form,
            'coupon_form': coupon_form,
            "total_after_discount": total_after_discount,  
            "discount": discount,  
            'discount_percentage': discount_percentage,
        })


def billing_info(request):
    if request.POST :
        cart = Cart(request)
        cart_products = cart.get_products()
        product_qty = cart.get_qty_for_product()
        total = cart.total() 
        shipping_price = 10 
        finally_price = None
        if cart.get_total_price_after_discount and cart.get_discount:
            finally_price = cart.get_total_price_after_discount 
        else :    
            finally_price = shipping_price + total

        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        host = request.get_host()
        my_invoice = str(uuid.uuid4())

        # create paypal form dic 
        paypal_dict = {
            'business' : settings.PAYPAL_RECEIVER_EMAIL,
            'amount': finally_price,
            'item_name': 'Book Order',
            'no_shipping': '2',
            'invoice': my_invoice,
            'currency_code': 'USD',
            'notify_url': 'https://{}{}'.format(host, reverse("paypal-ipn")),
            'return_url': 'https://{}{}'.format(host, reverse("payment_success")),
            'cancel_return': 'https://{}{}'.format(host, reverse("payment_failed")),  
        }

        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        if request.user.is_authenticated:
            billing_form = PaymentForm()

            my_shipping = request.session.get('my_shipping')

            # Get order info 
            full_name = my_shipping['full_name']
            email = my_shipping['email']
        
            # Create Shipping Address from session info
            shipping_address = f"{my_shipping['address1']}\n{my_shipping['address2']}\n{my_shipping['city']}\n{my_shipping['state']}\n{my_shipping['zipcode']}\n{my_shipping['country']}"
            amount_paid = finally_price
            user = request.user
            create_order = Order(
                                user=user, 
                                full_name=full_name,
                                email=email, 
                                amount_paid=amount_paid, 
                                shipping_adderss=shipping_address,
                                invoice = my_invoice,
                                )
            create_order.save()

            # Add Order Item 
            # Get Order Item Info
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price    
                for key, value in product_qty.items():
                    if int(key) == product.id :
                        quantity = value 
                        # Create Order Item 
                        create_order_item = OrderItem(
                                                    user=user,
                                                    order_id=order_id,
                                                    product_id=product_id,
                                                    quantity=quantity,
                                                    price=price
                                                    )   
                        create_order_item.save()
            
            # Delete Cart from DB (old_cart field)
            current_user = CustomerProfile.objects.filter(user__id = request.user.id)
            current_user.update(old_cart="")

            return render(request, "payment/billing_info.html", {"cart_products":cart_products, 
                                                            "product_qty":product_qty, 
                                                            "total":total, 
                                                            "shipping_form":request.POST ,
                                                            'finally_price' :finally_price,
                                                            'billing_form' : billing_form ,
                                                            'paypal_form' : paypal_form,
                                                          
                                                        })
        else :
            # Not logged in  
            create_order = Order(
                                user=user, 
                                full_name=full_name,
                                email=email, 
                                amount_paid=amount_paid, 
                                shipping_adderss=shipping_address,
                                invoice = my_invoice,
                                )
            create_order.save()
            create_order_item = OrderItem(
                                         user=user,
                                         order_id=order_id,
                                         product_id=product_id,
                                         quantity=quantity,
                                         price=price
                                        )   
            create_order_item.save()
            
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products":cart_products, 
                                                            "product_qty":product_qty, 
                                                            "total":total, 
                                                            "shipping_form":request.POST ,
                                                            'finally_price' :finally_price,
                                                            'billing_form' : billing_form,
                                                            'paypal_form' : paypal_form,
                                                          
                                                           })
    else:
        messages.success(request,'Access Denied')
        return redirect('home')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products()
        product_qty = cart.get_qty_for_product()
        total = cart.total() 
        shipping_price = 10 
        finally_price = shipping_price + total
        payment_form = PaymentForm(request.POST)
        my_shipping = request.session.get('my_shipping')

        # Get order info 
        full_name = my_shipping['full_name']
        email = my_shipping['email']
       
        # Create Shipping Address from session info
        shipping_address = f"{my_shipping['address1']}\n{my_shipping['address2']}\n{my_shipping['city']}\n{my_shipping['state']}\n{my_shipping['zipcode']}\n{my_shipping['country']}"
        amount_paid = finally_price

        # Create Order
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(
                                user=user, 
                                full_name=full_name,
                                email=email, 
                                amount_paid=amount_paid, 
                                shipping_adderss=shipping_address
                                )
            create_order.save()

           # Add Order Item 
           # Get Order Item Info
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price    
                for key, value in product_qty.items():
                    if int(key) == product.id :
                        quantity = value 
                        # Create Order Item 
                        create_order_item = OrderItem(
                                                      user=user,
                                                      order_id=order_id,
                                                      product_id=product_id,
                                                      quantity=quantity,
                                                      price=price
                                                      )   
                        create_order_item.save()
            # Delete Your Cart 
            for key in list(request.session.keys()):
                if key == 'cart':
                    del request.session[key]

            # Delete Cart from DB (old_cart field)
            current_user = CustomerProfile.objects.filter(user__id = request.user.id)
            current_user.update(old_cart="")
           
            messages.success(request,'Order placed...')
            return redirect('home')
        else:
            # not login 
            create_order = Order(           
                              full_name=full_name,
                              email=email, 
                              amount_paid=amount_paid, 
                              shipping_adderss=shipping_address
                              )
            create_order.save()

           # Add Order Item 
           # Get Order Item Info
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price    
                for key, value in product_qty.items():
                    if int(key) == product.id :
                        quantity = value 
                        # Create Order Item 
                        create_order_item = OrderItem(
                                                      order_id=order_id,
                                                      product_id=product_id,
                                                      quantity=quantity,
                                                      price=price
                                                      )   
                        create_order_item.save()
            messages.success(request,'Order placed...')
            return redirect('home')

    else:
        messages.success(request,'Access Denied...')
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            now = datetime.datetime.now()

            order = Order.objects.filter(id=num) 

            order.update(shipped=False)

            messages.success(request, 'Shipping status Updated')
            return redirect('home')
        return render(request, "payment/shipped_dash.html", {'orders':orders})
    else:
        messages.success(request,'Access Denied')
        return redirect('home')


def un_shipped_dash(request):
   
   if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            now = datetime.datetime.now()

            order = Order.objects.filter(id=num) 

            order.update(shipped=True,date_shipped=now)

            messages.success(request, 'Shipping status Updated')
            return redirect('home')
        return render(request, "payment/un_shipped_dash.html", {'orders':orders})
   else:
        messages.success(request,'Access Denied')
        return redirect('home')


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(pk=pk)
        order_items = OrderItem.objects.filter(order=order)

        if request.POST:
          status = request.POST['shipping_status']

          if status == 'true':
              order = Order.objects.filter(id=pk) 
              now = datetime.datetime.now()
              order.update(shipped=True,date_shipped=now)
          else:
              order = Order.objects.filter(id=pk) 
              order.update(shipped=False)

          messages.success(request, 'Shipping status Updated')
          return redirect('home')

        return render(request, "payment/orders.html", {
                                                        'order': order,
                                                        'orderitems': order_items
                                                    })
    else:
        messages.success(request, 'Access Denied')
        return redirect('home')


def payment_success(request):
    # Delte cart from  Browser 
    for key in list(request.session.keys()):
        if key == 'cart':
            del request.session[key]

    # Delete Cart from DB (old_cart field)
    current_user = CustomerProfile.objects.filter(user__id = request.user.id)
    current_user.update(old_cart="")
    return render(request,'payment/payment_success.html',{})


def payment_failed(request):
    return render(request,'payment/payment_failed.html',{})

# @require_POST
# def apply_coupon(request):
    
    
#    pass