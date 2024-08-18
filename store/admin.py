from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(CustomerProfile)


# Mix profile info and user info
class ProfileInline(admin.StackedInline):
	model = CustomerProfile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
	model = User
	field = '__all__'
	inlines = [ProfileInline]


admin.site.unregister(User)


admin.site.register(User, UserAdmin)