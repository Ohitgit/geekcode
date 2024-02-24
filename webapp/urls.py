
from django.urls import path
from .views import *

urlpatterns = [
    path("", home ,name="home"),
    path("coursedetailes/<str:slug>",coursedetailes ,name="coursedetailes"),
    path("course/<str:slug>",course ,name="course"),
    path("devlopment/<str:slug>",devlopment ,name="devlopment"),
    path("webdevlopment/<str:slug>",webdevlopment ,name="webdevlopment"),
    path("language/<str:slug>",language ,name="language"),
    path("signup",signup,name="signup"),
    path("login",logins,name="login"),
    path("logout",logout_view,name="logout"),
    path("addcart/<str:course_id>",addcart,name="addcart"),
   
    path("cart",cart,name="cart1"),
    
    path("deletecart",deletecart,name="deletecart"),
    path('order',orders ,name="order"),
     path('guestuser',guestuser ,name="guestuser"),
    path('order_received',verify ,name="order_received"),
    path('orderreceived',userverify,name="userverify"),
    path('user_dashboard',user_dashboard ,name="user_dashboard"),
    path('serach/<str:search>',serach,name="serach"),
    path('categoryserach/<str:search>',categoryserach,name="categoryserach"),
    path('forgot', forgot, name='forgot'),
  
    path('page', page, name='page'),
  
    path('course_list',course_list,name="course_list"),
    path('change-password/<str:token>',changepassword, name='change_password'),

   
    path('otp',otp,name="otp"),
    path('changeemail',changeemail,name="changeemail"),
    path('demo',demo,name='demo'),
    path('emailexists',emailexists,name='emailexists'),
    path('guestlogin/<str:order_id>',guestlogin,name="guestlogin"),
    path('userprofile',userprofile,name='userprofile'),
    path('change-password',profilechangepassword,name="changepassword"),
    path('emailverify',emaliverify,name="emailverify")
   
]