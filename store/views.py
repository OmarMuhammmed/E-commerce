from django.shortcuts import render
from .models import Product,Category,CustomerProfile
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm,UpdatePasswordForm,UserInfoForm
from django.contrib.auth import update_session_auth_hash
import json
from cart.cart import Cart
from payment.models import ShippingAdderss
from payment.forms import ShippingInfoForm

def home(request):
    products = Product.objects.all()
    # For Search 
    if 'search_name' in request.GET:
        name = request.GET['search_name']
        if name:
            products = products.filter(name__icontains=name)
    
    if 'search_name' in request.GET and not products.exists():
      messages.info(request, 'That Product Does Not Exist, Please Try Again....')

    return render(request, 'home.html', {'products': products})


def about(request):
    
    return render(request,'about.html',{})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None :
            login(request,user)

            current_user = CustomerProfile.objects.get(user__id= request.user.id )
            carty = current_user.old_cart 
            if carty:
              # Convert to dictionary using JSON
              converted_cart = json.loads(carty)
              cart = Cart(request)
              for key,value in converted_cart.items():
                cart.db_add(product=key, quantity=value)

            messages.success(request, ("You Have Been Logged In!"))
            return redirect('home')
        else :
            messages.error(request,'there was an error, please tr again ...')
            return redirect('login')
     
    else :
      return render(request,'login.html',{})
    
@login_required
def logout_user(request):
    messages.success(request,'You have been Logged out  thanks !')
    logout(request)
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method =='POST':
       form = SignUpForm(request.POST)
       if form.is_valid():
           form.save()
           username = form.cleaned_data['username']     
           password = form.cleaned_data['password1']
           # Login
           user = authenticate(username=username, password=password)
           login(request,user)   
           messages.success(request,'You have been registerted Succussfully, Welcome ! , Please Fill Out Your User Info Below... ')
           return redirect('update_info')
       else:
           messages.error(request,'Opps ! there was an error, please tr again ...') 
           return redirect('register')
    else:
      return render(request,'register.html',{'form':form})

@login_required
def update_user(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateUserForm(request.POST,instance=user) 
        if form.is_valid():
            form.save()  
            messages.success(request,'You have been Updated Profile Succussfully !')
            return redirect('home')
    else:
        form = UpdateUserForm(instance=user)    
     
    return render(request,'update_user.html',{'form':form})

@login_required
def update_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']  
            user = authenticate(username=request.user.username, password=current_password)
            if user:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # To confrim user not logout becuese password is changed
                messages.success(request, 'You have  updated your password successfully !')
                return redirect('home')
            else:
                form.add_error('current_password', 'Current password is incorrect')
    else:
        form = UpdatePasswordForm()
    
    return render(request, 'update_password.html', {'form': form})

@login_required
def update_info(request) :
    user = CustomerProfile.objects.get(user__id = request.user.id)
    shipping_user =ShippingAdderss.objects.get(user__id=request.user.id) 
    if request.method == 'POST':
        form = UserInfoForm(request.POST,instance=user) 
        shipping_form = ShippingInfoForm(request.POST,instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid() :
            form.save()  
            shipping_form.save()
            messages.success(request,'You have been Updated Profile Info Succussfully !')
            return redirect('home')
    else:
        shipping_form = ShippingInfoForm(instance=shipping_user)
        form = UserInfoForm(instance=user)    
    return render(request,'update_info.html',{'form':form,
                                               'shipping_form':shipping_form
                                              })   
   
def product(requset,id):
    product = Product.objects.get(id=id) 
    return render(requset,'product.html',{'product':product})

def category(request, foo):
	# Replace Hyphens with Spaces
	foo = foo.replace('-', ' ')
	# Grab the category from the url
	try:
		# Look Up The Category in DB 
		category = Category.objects.get(name=foo)
		products = Product.objects.filter(category=category)
		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.error(request, ("That Category Doesn't Exist..."))
		return redirect('home')

def category_summary(request):
     catagory = Category.objects.all()
     return render(request, 'category_summary.html',{
                                                    'catagory':catagory,
                                                    })

