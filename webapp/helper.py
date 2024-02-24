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
    course=Course.objects.values_list('name',flat=True)
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

def singup(request):
    if request.method == "POST":
       first=request.POST.get('first')
       mobile=request.POST.get('mobile')
       email=request.POST.get('email')
       password1=request.POST.get('password')
       try:
            User.objects.get(username=email)
            context={'error':'User Already Exists'}
            return render(request,'webapp/singup.html',context)
       except:
            password=make_password(password1)
            user=User.objects.create(username=email,password=password,first_name=first,last_name=mobile)
            Profile.objects.create(user=user)
            # Util.send_email(request,user.username)
            if user:
              return redirect('login')
    return render(request,'webapp/singup.html')


def logins(request):
     if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
    
        if user is not None :
         try:
              print('okkk')
              carts=Cart.objects.get(cart_id=cart_sessions(request))
              print('carts',carts)
              cart=CartItem.objects.filter(cart=carts).exists
              if cart:
               cart1=CartItem.objects.filter(cart=carts)
               for item in cart1:
                  item.user=user
                  item.save()
         except:
            pass

         login(request, user)
            
         return redirect('home')  
        else:
            context={'error':'invalid credentials'}
            return render(request,'webapp/login.html',context)
     return render(request,'webapp/login.html')

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
    course=Course.objects.filter(subcategory__in=[ x.id for x in subcategory ])
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
    try:
       if request.user.is_authenticated:
         
           cartitem1=CartItem.objects.filter(user=request.user)
          
           cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
           print('cart1',cart1)
           cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
           cartitem=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],course__name=course.name).exists()
           print('cartitem0',cartitem)
       else:
            carts=Cart.objects.get(cart_id=cart_sessions(request))
            cart=CartItem.objects.filter(cart=carts).count()
            cartitem=CartItem.objects.filter(cart=carts,course__name=course.name).exists()
    except Cart.DoesNotExist:
           carts=None
    context={'course':course,'category':category,'cart':cart,'cartitem':cartitem}
    return render(request,'webapp/couresdetailes.html',context)



def addcart(request,course_id):
      print('course',course_id)
      price=request.POST.get('price')
      Course.objects.get(id=course_id)
      
      if request.user.is_authenticated:
      
         cartitem1=CartItem.objects.filter(user=request.user)
         if Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1]).exists():
            cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1]).first()
            CartItem.objects.create(user=request.user,course_id=course_id,cart=cart1,price=price)
        
         else:
             if Cart.objects.filter(cart_id=cart_sessions(request)).exists() :
                  carts=Cart.objects.get(cart_id=cart_sessions(request))
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
       total_price1=sum(x.price for x in cartitems)
     else:
       carts=Cart.objects.get(cart_id=cart_sessions(request))
       cartitems=CartItem.objects.filter(cart=carts)
       cart=CartItem.objects.filter(cart=carts).count()
       total_price1=sum(x.price for x in cartitems)
 except Cart.DoesNotExist :
          pass
 currency = 'INR'
 total_amount_gst2=total_price1*18/100
 amount=(total_price1+total_amount_gst2)
 print(amount)
 razorpay_order = razorpay_client.order.create(dict(amount=amount*100, currency=currency,payment_capture='0'))
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
                  total_price=sum(x.price for x in cartitems)
                  cart=CartItem.objects.filter(user=request.user).count()
            else:
                  CartItem.objects.get(id=ids).delete()
                  carts=Cart.objects.get(cart_id=cart_sessions(request))
                  cartitems=CartItem.objects.filter(cart=carts)
                  total_price=sum(x.price for x in cartitems)
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
        #    carts=Cart.objects.get(user=request.user)
           cartitem1=CartItem.objects.filter(user=request.user)
           cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
           cartitems=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user)
        #    cartitems=CartItem.objects.filter(cart=carts)
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
        request.session['guestuser']=pro.email
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
            
           
            for x in allorders:
                x.status="approved"
                x.payment_id= payment_id
                x.save()
            total_amount=sum(i.total_price for i in allorders)
            amount_gst=total_amount*18/100
            amount=total_amount+amount_gst
            try:
                CartItem.objects.filter(order_id=razorpay_order_id).delete()
                razorpay_client.payment.capture(payment_id, amount*100)
                pro=Profile.objects.filter(order_id=razorpay_order_id).first()
                
              
                instance=User.objects.create(username=pro.email,first_name=pro.name,password=pro.password)
                pro.user=instance
                pro.save()
                approved_orders=order.objects.filter(order_id=razorpay_order_id)
                for i in approved_orders:
                    i.user=instance
                    i.save()
                orders=order.objects.filter(user=instance).first()
                Util.orderpurchesemail(request,orders)
                return redirect('user_dashboard')
                # return render(request, 'webapp/userdashboard.html',context)
                   
            except Exception as e:
                    print(e)
                    return render(request, 'webapp/paymentfail.html')
        else:
            return render(request, 'webapp/paymentfail.html')
        
   return redirect('demo')  

def user_dashboard(request):
    
    order_id= request.session.get('razorpay_order_id')
    allorders=order.objects.filter(order_id=order_id)
    user=request.session.get('guestuser')
    
    profile=Profile.objects.get(email=user)
    otp=request.session.get('otp')
    cat=Category.objects.all()

    sub=SubCategory.objects.all()
    course=Course.objects.all()
    allcourse= list(sub)  + list(cat) + list(course)
    context={'allorders':allorders,'otp':otp,'profile':profile,'allcourse':allcourse}

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
         profile=Profile.objects.filter(user__username=orders.user.username).first()
       
         for x in allorders:
             x.status="approved"
             x.payment_id= payment_id
             x.save()
         total_amount=sum(i.total_price for i in allorders)
         amount_gst=total_amount*18/100
         amount=total_amount+amount_gst
         try:
           razorpay_client.payment.capture(payment_id, amount*100)

           context={'allorders':allorders ,'amount':amount,'orders':orders}
           Util.orderpurchesemail(request,orders)
           return redirect('authuser_dashboard')
         except Exception as e:
                    print(e)
                    return render(request, 'webapp/paymentfail.html')
      else:
          return render(request, 'webapp/paymentfail.html')


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def authuser_dashboard(request):
    user=request.session.get('username')
    cat=Category.objects.all()
    sub=SubCategory.objects.all()
    course=Course.objects.all()
    allcourse= list(sub)  + list(cat) + list(course)
    try:

      if request.user.is_authenticated:   
        profile=Profile.objects.get(user=request.user)
        allorders1=order.objects.filter(user=request.user,status="approved")
        orders=order.objects.filter(user=request.user).first()
        items_per_page = 5
        paginator = Paginator(allorders1, items_per_page)
      else:
          profile=Profile.objects.get(user__username=user)
          allorders1=order.objects.filter(user__username=user,status="approved")
          orders=order.objects.filter(user__username=user).first()
          items_per_page = 5
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
          order_id= request.session.get('razorpay_order_id')
          allorders=order.objects.filter(order_id=order_id)
          user=request.session.get('guestuser')
          profile=Profile.objects.get(email=user)
          otp=request.session.get('otp')
          context={'allorders':allorders,'otp':otp,'profile':profile,'allcourse':allcourse}

    return render(request,'userdashboard/authuser_dashboard.html',context)

def serach(request,search):
   
   if Category.objects.filter(name__icontains=search).exists():
     cat=Category.objects.filter(name__icontains=search)
     subcategory=SubCategory.objects.filter(category__in=[x.id for x in cat])
     course=Course.objects.filter(subcategory__in=[ x.id for x in subcategory ])
     category=Category.objects.all()
     cart=''
     if request.user.is_authenticated:
       cartitem1=CartItem.objects.filter(user=request.user)
       cart1=Cart.objects.filter(cart_id__in=[x.cart for x in cartitem1])
       cart=CartItem.objects.filter(cart__cart_id__in=[i.cart_id for i in cart1],user=request.user).count()
     else:
        pass
    #  cart=Cart.objects.filter(user=request.user).count()
     context={'course':course,'category':category,'cart':cart}
     return render(request,'webapp/course.html',context)
   elif SubCategory.objects.filter(name__icontains=search).exists():
         subcategory=SubCategory.objects.filter(name__icontains=search)
         course=Course.objects.filter(subcategory__in=[ x.id for x in subcategory ])
         category=Category.objects.all()
        #  cart=Cart.objects.filter(user=request.user).count()
         context={'course':course,'category':category}
         return render(request,'webapp/course.html',context)
   elif Course.objects.filter(name__icontains=search).exists():
        
         course=Course.objects.filter(name__icontains=search)
        #  cart=Cart.objects.filter(user=request.user).count()
         category=Category.objects.all()
         context={'course':course,'category':category}
         return render(request,'webapp/course.html',context)
   else:
        return render(request,'webapp/coming-soon.html')   




def devlopment(request,slug):
    if Category.objects.filter(slug=slug).exists():
     cat=Category.objects.filter(slug=slug)
     subcategory=SubCategory.objects.filter(category__in=[x.id for x in cat])
     course=Course.objects.filter(subcategory__in=[ x.id for x in subcategory ])
     context={'course':course}
     return render(request,'webapp/course.html',context)
    else:
         return render(request,'webapp/coming-soon.html')

    
def webdevlopment(request,slug):
    if SubCategory.objects.filter(slug=slug).exists():
         subcategory=SubCategory.objects.filter(slug=slug)
         course=Course.objects.filter(subcategory__in=[ x.id for x in subcategory ])
         context={'course':course}
         return render(request,'webapp/course.html',context)
    else:
        return render(request,'webapp/coming-soon.html')


def language(request,slug):
    if Course.objects.filter(slug=slug).exists():
        
         course=Course.objects.filter(slug=slug)
         context={'course':course}
         return render(request,'webapp/course.html',context)
    else:
        return render(request,'webapp/coming-soon.html')  




def page(request):
    return render(request,'webapp/404.html')



def invoice_pdf(request,order_id):
    orders=order.objects.filter(order_id=order_id)
    orders1=order.objects.filter(order_id=order_id).first()
    profile=Profile.objects.filter(user__username=orders1.user.username).first()
    total_amount=sum(x.total_price for x in orders)
    amount_gst=total_amount*18/100
    amount=total_amount+amount_gst
    template_path = "pdf/invoice.html"
    print('template_path',template_path)
    context = {'orders':orders,'profile':profile,'amount':amount}  
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response





import random

def user_email_verfication(request):
        order_id=request.session.get('razorpay_order_id')
        if request.method == "POST":
            email=request.POST.get('email')
            try:
               user=User.objects.get(username=email)
               print('user',user)
               otp = random.randint(100000, 999999)
               request.session['otp']=otp
               request.session['useremail']=email
               Util.user_email_verfication(request,user,otp)
               messages.success(request, 'An email sent!')
               return redirect('otp')
            except Exception as e:
                 print(e)
                 messages.success(request, 'Email Does Not Exists')
                 context={'orders':order_id}
                 return redirect('user_dashboard')


def otp(request):
    order_id=request.session.get('razorpay_order_id')
    print('order-id',order_id)
    if request.method=="POST":
        otp1=request.POST.get('otp')
        print('otp1',otp1)
        otp=request.session.get('otp')
        print('otp',otp)
        if int(otp) == int(otp1):
            messages.success(request, 'Email Verify Succesfully..')
            return redirect('otp')
        else:
            messages.success(request, ' Please valid Email..')
            return redirect('otp')
    return render(request,"userdashboard/otp.html")





def changeemail(request):
    if request.method =="POST":
        email=request.POST.get('email')
        useremail=request.session.get('useremail')
        print('user',useremail)
        try:
            user=User.objects.get(username=useremail)
            pro=Profile.objects.get(user=user)
            pro.email=email
            pro.save()

            user.username=email
            user.save()

          
            del request.session['useremail']
            messages.success(request, 'Update Your Email')

            return redirect('changeemail')
        except User.DoesNotExist:
            
            return redirect('home')
    return render(request,"userdashboard/changeemail.html")



def emailexists(request):
    email=request.GET.get('email')
    if User.objects.filter(username=email).exists():
        data={'msg':True}
      
    else:
        data={'msg':False}
    return JsonResponse(data)



def demo(request):
    return render(request,'userdashboard/orderemail.html')




def userprofile(request):
   user=request.session.get('username')
   try:
      # Try to get the profile based on the provided username
     profile = Profile.objects.get(user__username=user)

   except Profile.DoesNotExist:
     try:
        if request.user.is_authenticated:
          profile = Profile.objects.get(user=request.user)
        else:
             user = request.session.get('guestuser')
             profile = Profile.objects.get(email=user)
     except Profile.DoesNotExist:
       
        user = request.session.get('guestuser')
        profile = Profile.objects.get(email=user)

        try:
            profile = Profile.objects.get(email=user)
        except Profile.DoesNotExist:
            
            print("Profile does not exist for the given user or email")

    
   return render(request,"userdashboard/userprofile.html",{'profile':profile})



def photo(request):
    user=request.session.get('username')
    try:
        if request.user.is_authenticated:
          profile = Profile.objects.get(user=request.user)
        else:
            profile=Profile.objects.get(user__username=user)
    except Profile.DoesNotExist:
        user=request.session.get('guestuser')
        profile=Profile.objects.get(email=user)

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
    
    return render(request,"userdashboard/photo.html",{'profile':profile})


def profilechangepassword(request):
    
    try:
        
        if request.user.is_authenticated:
          profile = Profile.objects.get(user=request.user)
          user=profile.user.username
        else:
            user=request.session.get('username')
            profile=Profile.objects.get(user__username=user)
    except Profile.DoesNotExist:
        user=request.session.get('guestuser')
        profile=Profile.objects.get(email=user)
    if request.method =="POST":
        oldpassword=request.POST.get('oldpassword')
        newpassword=request.POST.get('newpassword')
       
        user=authenticate(username=user,password=oldpassword)
        if user:
            user.set_password(newpassword)
            user.save()
            return redirect('login')

    return render(request,"userdashboard/chagepassword.html",{'profile':profile})
