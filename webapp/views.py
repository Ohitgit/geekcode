from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
import razorpay
from .utils import *
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from razorpay.errors import BadRequestError
from .forms import *
razorpay_client = razorpay.Client(
    auth=(settings.ROZARPAY_KEY, settings.RAZOR_KEY_SECRET))
# Create your views here.
def cart_sessions(request):
    carts=request.session.session_key 
    if not carts:
       carts=request.session.create()
    return carts  
    

    
def course_list(request):
    cat=Category.objects.values_list('name',flat=True)

    sub=SubCategory.objects.values_list('name',flat=True)
    course=Language.objects.values_list('name',flat=True)
    allcourse= list(sub)  + list(cat) + list(course)
    return JsonResponse(allcourse ,safe=False)
    

def home(request):
   category=Category.objects.all()
   # cart=Cart.objects.filter(user=request.user).count()
   context={'category':category}
   return render(request,'webapp/index.html',context)

def logout_view(request):
    logout(request)
    return redirect('login')


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            first = form.cleaned_data['first']
            mobile = form.cleaned_data['mobile']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password']
            checkbox = form.cleaned_data['checkbox']

            try:
                User.objects.get(username=email)
                context = {'error': 'User Already Exists'}
                return render(request, 'webapp/signup.html', context)
            except User.DoesNotExist:
                password = make_password(password1)
                user = User.objects.create(username=email, password=password, first_name=first, last_name=mobile)

                if checkbox:
                    Profile.objects.create(user=user, checkbox=True)
                else:
                    Profile.objects.create(user=user, checkbox=False)

                # Util.send_email(request, user.username)
                if user:
                    return redirect('login')

    else:
        form = SignupForm()

    return render(request, 'webapp/signup.html', {'form': form})


def logins(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
              
                try:
                    print('okkk')
                    carts = Cart.objects.get(cart_id=cart_sessions(request))
                    print('carts', carts)
                    cart_exists = CartItem.objects.filter(cart=carts).exists()
                    if cart_exists:
                        cart_items = CartItem.objects.filter(cart=carts)
                        for item in cart_items:
                            item.user = user
                            item.save()
                except:
                    pass

                login(request, user)
                return redirect('home')
            else:
                form = LoginForm()

                context = {'error': 'Invalid credentials','form':form}
                return render(request, 'webapp/login.html', context)
    else:
        form = LoginForm()

    return render(request, 'webapp/login.html', {'form': form})

def changepassword(request,token):
    
     if request.method== "POST":
         newpassword=request.POST.get('newpassword')
         print('new',newpassword)
         password=request.POST.get('password')
         if newpassword != password:
            messages.success(request, 'password not match')
            current_url=request.get_full_path()
            return redirect(current_url)
         else:
             obj=Profile.objects.get(token=token)
             user=User.objects.get(id=obj.user.id)
             evals=user.set_password(newpassword)
             print('evals',evals)
             user.save()
             return redirect('login')
     return render(request,"webapp/changepassword.html")

import uuid    
def forgot(request):
  
        if request.method== "POST":
            email=request.POST.get('email')
            email1=User.objects.get(username=email)
            
            if User.objects.get(username=email):
                obj=Profile.objects.get(user_id=email1.id)
                uuids=str(uuid.uuid4())
                obj.token=uuids
                obj.save()
                current_site=get_current_site(request=request).domain
                
                relativelink=reverse('change_password',kwargs={'token':uuids})
                absurl='http://'+current_site + relativelink
                email_body='Hello, \n Use link below to reset your password  \n' + absurl

                data={'email_body':email_body,'to_email':email1.email,'email_subject':'Reset your email'}
               
                Util.forget_email(data)
                # send_forget_password_email(email1,token)
                messages.success(request, 'An email sent!')
                return redirect('forgot')
        return render(request,"webapp/forget.html")    

  
def course(request,slug):
    category=Category.objects.all()
    
    cat=Category.objects.get(slug=slug)
    subcategory=SubCategory.objects.filter(category=cat)
    course=Course.objects.filter(languge__subcategory__in=( x.id for x in subcategory ))
    cart=None
    try:
         if request.user.is_authenticated:
         
           cartitem=CartItem.objects.filter(user=request.user)
           print('caert',cartitem)
           cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem])
           print('cart1',cart1)
           cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
           
         else:
              carts=Cart.objects.get(cart_id=cart_sessions(request))
              print('carts44',carts)
              cart=CartItem.objects.filter(cart=carts).count()
    except Cart.DoesNotExist:
           carts=None
    
    context={'course':course,'category':category,'cart':cart}
    return render(request,'webapp/course.html',context)


def coursedetailes(request,slug):
    category=Category.objects.all()
    course=Course.objects.get(slug=slug)
    cart=None
    cartitem=None
    orders=None
    try:
       if request.user.is_authenticated:
           try:
              orders=order.objects.get(user=request.user,course__title=course.title)
              print('orders',orders)
           except order.DoesNotExist:
                orders=None
           cartitem1=CartItem.objects.filter(user=request.user)
          
           cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
           print('cart1',cart1)
           cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
           cartitem=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],course__title=course.title).exists()
           print('cartitem0',cartitem)
       else:
            carts=Cart.objects.get(cart_id=cart_sessions(request))
            cart=CartItem.objects.filter(cart=carts).count()
            cartitem=CartItem.objects.filter(cart=carts,course__title=course.title).exists()
    except Cart.DoesNotExist:
           carts=None
    context={'course':course,'category':category,'cart':cart,'cartitem':cartitem,'orders':orders}
    return render(request,'webapp/couresdetailes.html',context)



def addcart(request,course_id):
      print('course',course_id)
      price=request.POST.get('price')
      Course.objects.get(id=course_id)
      
      if request.user.is_authenticated:
      
         cartitem1=CartItem.objects.filter(user=request.user)
         if Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1]).exists():
            print('okk cartitem')
            cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1]).first()
            CartItem.objects.create(user=request.user,course_id=course_id,cart=cart1,price=price)
        
         else:
             print('okkk-------no')
             if Cart.objects.filter(cart_id=cart_sessions(request)).exists() :
                  
                  carts=Cart.objects.get(cart_id=cart_sessions(request))
                  CartItem.objects.create(user=request.user,course_id=course_id,cart=carts,price=price)
             else:
                  carts=Cart.objects.create(cart_id=cart_sessions(request))
                  CartItem.objects.create(user=request.user,course_id=course_id,cart=carts,price=price)
              
      else :
            if Cart.objects.filter(cart_id=cart_sessions(request)).exists():
                  carts=Cart.objects.get(cart_id=cart_sessions(request))
                  CartItem.objects.create(course_id=course_id,cart=carts,price=price)
            else:
                carts=Cart.objects.create(cart_id=cart_sessions(request))
                CartItem.objects.create(course_id=course_id,cart=carts,price=price)
                    
      return redirect('cart1')
      
    
     

def cart(request,total_price1=0,cartitems=None):
 try:
     
     if request.user.is_authenticated:
       user=User.objects.get(username=request.user)
       request.session['username']=user.username
       cartitem1=CartItem.objects.filter(user=request.user)
       cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
       cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
       cartitems=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user)
       cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitems])
       total_price1=int(sum(x.price for x in cartitems))
     else:
       carts=Cart.objects.get(cart_id=cart_sessions(request))
       cartitems=CartItem.objects.filter(cart=carts)
       cart=CartItem.objects.filter(cart=carts).count()
       total_price1=int(sum(x.price for x in cartitems))
 except Cart.DoesNotExist :
          pass
 currency = 'INR'
 total_amount_gst2=total_price1*18/100
 amount=int(total_price1+total_amount_gst2)
 
 print(amount)
 try:
     razorpay_order = razorpay_client.order.create(dict(amount=amount*100, currency=currency,payment_capture='0'))
 except BadRequestError as e:
     amount=1.00
     razorpay_order = razorpay_client.order.create(dict(
    amount=int(amount * 100),  # Convert to paisa
    currency='INR',
    payment_capture='0'
))
 razorpay_order_id = razorpay_order['id']
 request.session['razorpay_order_id'] = razorpay_order_id
 rozarpay_key=settings.ROZARPAY_KEY
 context={'carts':cartitems,'cart':cart,'total_price':amount,'razorpay_order_id':razorpay_order_id,'rozarpay_key':rozarpay_key,'currency':currency}
 return render(request,"webapp/cart1.html",context)



def deletecart(request):
     ids=request.GET.get('ids')
     if  CartItem.objects.filter(id=ids).exists():
            if request.user.is_authenticated:
                  CartItem.objects.get(id=ids).delete()
                  cartitems=CartItem.objects.filter(user=request.user)
                  total_price1=int(sum(x.price for x in cartitems))
                  total_amount_gst2=total_price1*18/100
                  total_price=int((total_price1+total_amount_gst2))
                  cart=CartItem.objects.filter(user=request.user).count()
            else:
                  CartItem.objects.get(id=ids).delete()
                  carts=Cart.objects.get(cart_id=cart_sessions(request))
                  cartitems=CartItem.objects.filter(cart=carts)
                  total_price1=int(sum(x.price for x in cartitems))
                  total_amount_gst2=total_price1*18/100
                  total_price=int((total_price1+total_amount_gst2))
                  cart=CartItem.objects.filter(cart=carts).count()
               
            data={'total_price':total_price,   'cart':cart }
            return JsonResponse(data)




#authcationuser
def orders(request):
    if request.method=='POST':
       email= request.POST.get('email')
       if Profile.objects.filter(user__username=email).exists():
           profile=Profile.objects.get(user__username=email)
           rozarpay_order= request.session.get('razorpay_order_id')
      
           cartitem1=CartItem.objects.filter(user=request.user)
           cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
           cartitems=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user)
        
           for x in cartitems:
              order.objects.create(user_id=profile.user.id,course_id=x.course.id,total_price=x.price,order_id=rozarpay_order)
           return JsonResponse({'msg':"Order sucessfully Added "})
          
    

def guestuser(request):
    if request.method=="POST":

        name=request.POST.get('name')
        email=request.POST.get('email')
        mobile=request.POST.get('mobile')
        password1=request.POST.get('password')
        password=make_password(password1)
      
        rozarpay_order= request.session.get('razorpay_order_id')
        pro=Profile.objects.create(order_id=rozarpay_order,name=name,email=email,mobile=mobile,password=password)
        carts=Cart.objects.get(cart_id=cart_sessions(request))
        cartitems=CartItem.objects.filter(cart=carts)
        for x in cartitems:
              x.order_id=rozarpay_order
              x.save()
              order.objects.create(course_id=x.course.id,total_price=x.price,order_id=rozarpay_order)
        return JsonResponse({'msg':"Order sucessfully Added "})


@csrf_exempt
def verify(request):
   if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
        result = razorpay_client.utility.verify_payment_signature(params_dict)
        if result is not None:
            allorders=order.objects.filter(order_id=razorpay_order_id)
            
           
           
            total_amount=int(sum(i.total_price for i in allorders))
            amount_gst=total_amount*18/100
            amount=int(total_amount+amount_gst)
            print('amount44',amount)
            try:
                CartItem.objects.filter(order_id=razorpay_order_id).delete()
                am=razorpay_client.payment.capture(payment_id, amount*100)
                print('amount',am)
                method=am['method']
                pro=Profile.objects.filter(order_id=razorpay_order_id).first()
                
              
                instance=User.objects.create(username=pro.email,first_name=pro.name,password=pro.password,last_name=pro.mobile)
                pro.user=instance
                pro.save()
                
                approved_orders=order.objects.filter(order_id=razorpay_order_id)
                for i in approved_orders:
                    i.user=instance
                    i.status="approved"
                    i.payment_id= payment_id
                    i.save()
                orders=order.objects.filter(user=instance).first()
                Util.orderpurchesemail(request,orders,method)
                # return redirect('user_dashboard')
                return redirect('guestlogin', order_id=orders.order_id)
                # return render(request, 'webapp/userdashboard.html',context)
                   
            except Exception as e:
                    print(e)
                    return render(request, 'webapp/paymentfail.html')
        else:
            return render(request, 'webapp/paymentfail.html')
        

  
def guestlogin(request,order_id):
    try:
      profile=Profile.objects.get(order_id=order_id)
    except Profile.DoesNotExist:
            return render(request,'webapp/404.html')
    user=User.objects.get(username=profile.user)
    login(request,user)
    try:
       verify=EmailVerfication.objects.get(email=user.username)
       print('verify',verify)
    except EmailVerfication.DoesNotExist:
          verify=None
    return render(request,"userdashboard/login.html",{'verify':verify})

def emaliverify(request):
    if request.method == 'POST':
      email=request.POST.get('email')
      user=User.objects.get(username=email)
      otp = random.randint(100000, 999999)
      request.session['otp']=otp
      Util.user_email_verfication(request,user,otp)
      return JsonResponse({'msg':'Verification code sent to your email...'})
    



def user_dashboard(request):
    allorders=order.objects.filter(user=request.user)
    try:
         profile=Profile.objects.get(email=request.user)
    except Profile.DoesNotExist:
          return render(request,'webapp/404.html')
   
    cat=Category.objects.all()

    sub=SubCategory.objects.all()
    # course=Language.objects.all()
    # print('course',course)
    allcourse= list(sub)  + list(cat) 
    context={'allorders':allorders,'profile':profile,'allcourse':allcourse}

    return render(request, 'userdashboard/userdashboard.html',context)   



#autica
@csrf_exempt
def userverify(request):
  if request.method == "POST":
      payment_id = request.POST.get('razorpay_payment_id', '')
      razorpay_order_id = request.POST.get('razorpay_order_id', '')
      signature = request.POST.get('razorpay_signature', '')
      params_dict = {  'razorpay_order_id': razorpay_order_id,  'razorpay_payment_id': payment_id,  'razorpay_signature': signature  }
      result = razorpay_client.utility.verify_payment_signature( params_dict)
      if result is not None:
         allorders=order.objects.filter(order_id=razorpay_order_id)
         orders=order.objects.filter(order_id=razorpay_order_id).first()
         carts=CartItem.objects.filter(user__username=orders.user.username).first()
         cart = Cart.objects.get(cart_id=carts.cart)
         cart.delete()
      
       
         for x in allorders:
             x.status="approved"
             x.payment_id= payment_id
             x.save()
         total_amount=int(sum(i.total_price for i in allorders))
         amount_gst=total_amount*18/100
         amount=int(total_amount+amount_gst)
         print('amount',amount)
         
         
         try:
           am=razorpay_client.payment.capture(payment_id, amount*100)
           print('am777',am['method'])
           method=am['method']
           Util.orderpurchesemail(request,orders,method)
           return redirect('user_dashboard')
         except Exception as e:
                    print(e)
                    return render(request, 'webapp/paymentfail.html')
      else:
          return render(request, 'webapp/paymentfail.html')


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def user_dashboard(request):
   
    # cat=Category.objects.all()
    # sub=SubCategory.objects.all()
    allcourse=Language.objects.all()
    # allcourse= list(sub)  + list(cat) + list(course)
    
    try:
        profile=Profile.objects.get(user=request.user)
        allorders1=order.objects.filter(user=request.user,status="approved")
        orders=order.objects.filter(user=request.user).first()
        items_per_page = 5
        paginator = Paginator(allorders1, items_per_page)
        paginator = Paginator(allorders1, items_per_page)
        page = request.GET.get('page', 1)
        try:
            allorders = paginator.page(page)
        except PageNotAnInteger:
            allorders = paginator.page(1)
        except EmptyPage:
            allorders = paginator.page(paginator.num_pages)
        context={'allorders':allorders,'user':orders,'profile':profile,'allcourse':allcourse}
    except:
          return render(request,'webapp/404.html')

    return render(request,'userdashboard/authuser_dashboard.html',context)

def serach(request,search):
   
   if Category.objects.filter(name__icontains=search).exists():
     cat=Category.objects.filter(name__icontains=search).values_list('id', flat=True)
     subcategory=SubCategory.objects.filter(category__in=cat).values_list('id', flat=True)
     course=Course.objects.filter(languge__subcategory__in=subcategory)
     category=Category.objects.all()
     cart=''
     if request.user.is_authenticated:
       cartitem1=CartItem.objects.filter(user=request.user)
       cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
       cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
       
     context={'course':course,'category':category,'cart':cart}
     return render(request,'webapp/course.html',context)
   elif SubCategory.objects.filter(name__icontains=search).exists():
         subcategory=SubCategory.objects.filter(name__icontains=search).values_list('id', flat=True)
         course=Course.objects.filter(languge__subcategory__in= subcategory)
         category=Category.objects.all()
         context={'course':course,'category':category}
         return render(request,'webapp/course.html',context)
   elif Course.objects.filter(languge__name__icontains=search).exists():
        
         course=Course.objects.filter(languge__name__icontains=search)
        #  cart=Cart.objects.filter(user=request.user).count()
         category=Category.objects.all()
         context={'course':course,'category':category}
         return render(request,'webapp/course.html',context)
   else:
        return render(request,'webapp/coming-soon.html')   




def categoryserach(request,search):
    # cat=Category.objects.all()
    # sub=SubCategory.objects.all()
    allcourse=Language.objects.all()

    if Course.objects.filter(languge__name=search).exists()   :   
        profile=Profile.objects.get(user=request.user)
        course1=Course.objects.filter(languge__name=search)
        allorders=order.objects.filter(user=request.user,course__languge__name__in=[x.languge.name for x in course1],status="approved")
        orders=order.objects.filter(user=request.user).first()
    context={'search':search,'allorders':allorders,'user':orders,'profile':profile,'allcourse':allcourse}
    return render(request,'userdashboard/authuser_dashboard.html',context)
    
       


def devlopment(request,slug):
    category=Category.objects.all()
    if Category.objects.filter(slug__icontains=slug).exists():
     cat=Category.objects.filter(slug__icontains=slug).values_list('id', flat=True)
     subcategory=SubCategory.objects.filter(category__in=cat).values_list('id', flat=True)
     course1=Language.objects.filter(subcategory__in= subcategory )
     course_names = course1.values_list('name', flat=True)
     course=Course.objects.filter(languge__name__in=  course_names)
     print('course',course)
     context={'course':course,'category':category}
     return render(request,'webapp/course.html',context)
    else:
         return render(request,'webapp/coming-soon.html')
   
def webdevlopment(request,slug):
    category=Category.objects.all()
    if SubCategory.objects.filter(slug__icontains=slug).exists():
        subcategory_ids = SubCategory.objects.filter(slug__icontains=slug).values_list('id', flat=True)
        course1 = Language.objects.filter(subcategory__in=subcategory_ids)
        course_names = course1.values_list('name', flat=True)
        course = Course.objects.filter(languge__name__in=course_names)
        context={'course':course,'category':category}
        return render(request,'webapp/course.html',context)
    else:
        return render(request,'webapp/coming-soon.html')


def language(request,slug):
    category=Category.objects.all()
    if Course.objects.filter(languge__name=slug).exists():
        
         course=Course.objects.filter(languge__name=slug)
         context={'course':course,'category':category}
         return render(request,'webapp/course.html',context)
    else:
        return render(request,'webapp/coming-soon.html')  




def page(request):
    return render(request,'webapp/404.html')

def otp(request):
    
    if request.method=="POST":
        otp1=request.POST.get('otp')
        print('otp1',otp1)
        otp=request.session.get('otp')
        print('otp',otp)
        if int(otp) == int(otp1):
          return JsonResponse({'msg':'Email Verify Succesfully..'})
        else:
           return JsonResponse({'error':'Please Valid Email Enter..'})

def changeemail(request):
    if request.method =="POST":
        oldemail=request.POST.get('oldemail')
        newemail=request.POST.get('newemail')
        try:
            EmailVerfication.objects.get(email=newemail)
        except EmailVerfication.DoesNotExist:
               EmailVerfication.objects.create(email=newemail,is_verify=True)
        user=User.objects.get(username=oldemail)
        pro=Profile.objects.get(user=user)
        pro.email=newemail
        pro.save()
        user.username=newemail
        user.save()
        return JsonResponse({'msg':'Update Your Email...'})
  
def emailexists(request):
    email=request.GET.get('email')
    if User.objects.filter(username=email).exists():
        data={'msg':True}
      
    else:
        data={'msg':False}
    return JsonResponse(data)



def demo(request):
    return render(request,'webapp/certificate.html')




def userprofile(request):

   try:
      # Try to get the profile based on the provided username
       if request.user.is_authenticated:
         profile = Profile.objects.get(user=request.user)
       else:
            return render(request,'webapp/404.html')
       if request.method == "POST":
        if request.FILES.get('img')== None:
            profile.image=profile.image
            profile.save()
            messages.success(request, 'Update Your Profile img')
        else:
          img=request.FILES.get('img')
          profile.image=img
          profile.save()
          messages.success(request, 'Update Your Profile img')
   except Profile.DoesNotExist:
       return render(request,'webapp/404.html')
   return render(request,"userdashboard/userprofile.html",{'profile':profile})






def profilechangepassword(request):
    
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
      return render(request,'webapp/404.html')
    if request.method =="POST":
        oldpassword=request.POST.get('oldpassword')
        newpassword=request.POST.get('newpassword')
       
        user=authenticate(username=request.user,password=oldpassword)
        if user:
            user.set_password(newpassword)
            user.save()
            return redirect('login')

    return render(request,"userdashboard/chagepassword.html",{'profile':profile})



def invoice_pdf(request,order_id):
    orders=order.objects.filter(order_id=order_id)
    orders1=order.objects.filter(order_id=order_id).first()
    image="/static/img/carousel/certificate.jpg"
    profile=Profile.objects.filter(user__username=orders1.user.username).first()
    
    template_path = "pdf/invoice.html"
    print('template_path',template_path)
    context = {'orders':orders,'profile':profile,'orders1':orders1,'image':image}  
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response





def privacypolicy(request):
    return render(request,'webapp/privacypolicy.html')

def accessibility(request):
    return render(request,'webapp/accessibility.html')


def careers(request):
    return render(request,'webapp/careers.html')


def helpsupport(request):
    return render(request,'webapp/helpsupport.html')



def aboutus(request):
    return render(request,'webapp/about-us.html')



def contact(request):
    return render(request,'webapp/contact.html')