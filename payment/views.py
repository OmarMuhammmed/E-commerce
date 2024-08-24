from django.shortcuts import render
from .forms import ShippingInfoForm,PaymentForm
from cart.cart import Cart
from .models import ShippingAdderss,Order,OrderItem
from django.shortcuts import redirect
from django.contrib import messages
from store.models import CustomerProfile, Product
import datetime
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    product_qty = cart.get_qty_for_product()
    total = cart.total() 
    shipping_price = 10 
    finally_price = shipping_price + total

    if request.user.is_authenticated:
        shipping_user = ShippingAdderss.objects.get(user__id=request.user.id)
        shipping_form = ShippingInfoForm(request.POST or None, instance=shipping_user)
        
        return render(request, "payment/checkout.html", {"cart_products":cart_products, 
                                                         "product_qty":product_qty, 
                                                         "total":total, 
                                                         "shipping_form":shipping_form,
                                                         'finally_price' :finally_price
                                                           })
    else :
        shipping_form = ShippingInfoForm(request.POST)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products,
                                                        'product_qty': product_qty,
                                                        'total': total,
                                                        'finally_price' :finally_price,
                                                        'shipping_form' :shipping_form
                                                        })


def billing_info(request):
    if request.POST :
        cart = Cart(request)
        cart_products = cart.get_products()
        product_qty = cart.get_qty_for_product()
        total = cart.total() 
        shipping_price = 5 
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
                                                            'paypal_form' : paypal_form
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

