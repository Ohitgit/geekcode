from django.core.mail import EmailMessage
from django.conf import settings as conf_settings
from django.template.loader import render_to_string
from django.core.mail import send_mail 
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
import uuid
import threading
import random
from .models import *

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    
    @staticmethod
    def send_email(request,user):
        mail_from = conf_settings.EMAIL_HOST_USER
        mail_to = user
        context_data = {
        'mail_from':mail_from,
        'mail_to': mail_to,
        }
        text_content = render_to_string('{0}/templates/webapp/singup_email.html'.format(conf_settings.BASE_DIR), context=context_data)
        email = EmailMultiAlternatives("Thank you for enquiry", text_content, conf_settings.EMAIL_HOST_USER, [mail_to])
        print('ggkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',email)
        email.attach_alternative(text_content, 'text/html')
        EmailThread(email).start()


        mail_from = conf_settings.EMAIL_HOST_USER
        mail_to = "mohitpatidar.1998.24@gmail.com"
        context_data = {
        'mail_from':mail_from,
        'mail_to': mail_to,
        }
        text_content = render_to_string('{0}/templates/webapp/singup_email.html'.format(conf_settings.BASE_DIR), context=context_data)
        email = EmailMultiAlternatives("Thank you for enquiry", text_content, conf_settings.EMAIL_HOST_USER, [mail_to])
        print('ggkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',email)
        email.attach_alternative(text_content, 'text/html')
        EmailThread(email).start()

    @staticmethod
    def forget_email(data):
        print('data',data)
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
    


    @staticmethod
    def user_email_verfication(request,user,otp):
        mail_from = conf_settings.EMAIL_HOST_USER
        mail_to = user.username
        
        context_data = {
        'mail_from':mail_from,
        'mail_to': mail_to,
         'otp':otp,
         'name':user.first_name
        }
        text_content = render_to_string('{0}/templates/webapp/user_email.html'.format(conf_settings.BASE_DIR), context=context_data)
        email = EmailMultiAlternatives("Email Verification ", text_content, conf_settings.EMAIL_HOST_USER, [mail_to])
        email.attach_alternative(text_content, 'text/html')
        EmailThread(email).start()

      
    @staticmethod
    def orderpurchesemail(request,orders,method):
        mail_from = conf_settings.EMAIL_HOST_USER
        mail_to = orders.user
        allorders=order.objects.filter(order_id=orders.order_id)
    
        
        profile=Profile.objects.filter(order_id=orders).first()
      
        total_amount=sum(i.total_price for i in allorders)
        amount_gst=total_amount*18/100
        amount=total_amount+amount_gst
        context_data = {
        'mail_from':mail_from,
        'mail_to': mail_to,
        'orders':orders,
        'allorders':allorders,
        'amount':amount,
        'profile':profile,
        'method':method
         
        }
        text_content = render_to_string('{0}/templates/userdashboard/orderemail.html'.format(conf_settings.BASE_DIR), context=context_data)
        email = EmailMultiAlternatives("order purchase confirmation ", text_content, conf_settings.EMAIL_HOST_USER, [mail_to])
        email.attach_alternative(text_content, 'text/html')
        EmailThread(email).start()

       

   






