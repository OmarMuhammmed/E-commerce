from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time 
from .models import Order

@receiver(valid_ipn_received) # func not run when payment success
def paypal_payment_received(sender,**kwargs):
    time.sleep(10) # wait 10 second before run a func

    ipn_obj = sender  # contain Data payment 
    my_invoice= str(ipn_obj.invoice)
    
    # Get the match invoice
    my_order = Order.objects.get(invoice=my_invoice)
    my_order.paid = True
    my_order.save()

                                     