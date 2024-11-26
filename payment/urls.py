from django.urls import path, include
from . import views

urlpatterns = [
    path('payment_success',views.payment_success, name='payment_success'),
    path('payment_failed',views.payment_failed, name='payment_failed'),
    path('checkout',views.checkout, name='checkout'),
    path('billing_info',views.BillingInfoView.as_view(), name='billing_info'),
    path('process_order',views.ProcessOrderView.as_view(), name='process_order'),
    path('shipped_dash',views.shipped_dash, name='shipped_dash'),
    path('un_shipped_dash',views.un_shipped_dash, name='un_shipped_dash'),
    path('orders/<int:pk>',views.orders, name='orders'),
    # path('apply_coupon/',views.apply_coupon, name='apply_coupon'),
    path('paypal/', include('paypal.standard.ipn.urls')),
]
