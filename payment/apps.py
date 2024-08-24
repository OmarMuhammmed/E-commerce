from django.apps import AppConfig


class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment'

    

    # config paypal IPN Signals
    def ready(self) : # Work aftar runserver  
        import payment.hooks
        