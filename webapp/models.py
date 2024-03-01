from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.conf import settings
import os
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True,null=True,db_index=True)
    image=models.FileField(null=True,db_index=True,upload_to='media/images/')

    def __str__(self):
        return   str(self.name)
@receiver(pre_save, sender=Category)
def create_slug(sender, instance, **kwargs):
      if not instance.slug:
        instance.slug = slugify(instance.name)

class SubCategory(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True,null=True,db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True,db_index=True)
    def __str__(self):
     return   str(self.name)

@receiver(pre_save, sender=SubCategory)
def create_slug(sender, instance, **kwargs):
      if not instance.slug:
        instance.slug = slugify(instance.name)


class Language(models.Model):
     name = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE,null=True,db_index=True)
     def __str__(self):
      return str(self.name)
from django.utils import timezone as tz
     
class Course(models.Model):
   
    
    slug = models.SlugField(max_length=255, unique=True, blank=True,null=True,db_index=True)
    title = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    author = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    rating = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    languge = models.ForeignKey(Language, on_delete=models.CASCADE,null=True,db_index=True)
    content=models.TextField(null=True)
    short_description=models.TextField(null=True)
    price = models.IntegerField(null=True,blank=True ,db_index=True)
    image=models.FileField(null=True,db_index=True,upload_to='course')
    datetime=models.DateTimeField(null=True,default=tz.now)
    def __str__(self):
      return str(self.title)
    
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)

        img=Image.open(self.image.path)
        if img.height > 600 and img.width > 800:
           output_size=(800,600)
           img.thumbnail(output_size)
           webp_output = BytesIO()
           img.save(webp_output, format='WebP')
           webp_output.seek(0)
           resized_webp_image_path = f"{self.image.name.replace('.jpg', '.webp')}"
           resized_webp_image_full_path = os.path.join(settings.MEDIA_ROOT, resized_webp_image_path)
           print('resize',resized_webp_image_full_path)
           os.makedirs(os.path.dirname(resized_webp_image_full_path), exist_ok=True)
           with open(resized_webp_image_full_path, 'wb') as webp_file:
            webp_file.write(webp_output.read())
           self.image.name = resized_webp_image_path
           super().save(*args, **kwargs)

# @receiver(pre_save, sender=Course)
# def create_slug(sender, instance, **kwargs):
#       if not instance.slug:
#         instance.slug = slugify(instance.title)


     
class Cart(models.Model):
   
    
    cart_id=models.CharField(null=True,blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
      return str(self.cart_id)



class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,db_index=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,null=True,db_index=True,related_name='member_of')
    order_id = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,db_index=True)
    price=models.IntegerField(null=True,blank=True,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    

    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,db_index=True)
    order_id = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    name = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    email = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    mobile = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    password = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    image=models.FileField(null=True,db_index=True,upload_to='media/images/')
    token = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    checkbox=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
      return str(self.name)

class order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,db_index=True)
    order_id = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    payment_id = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,null=True,db_index=True)
    total_price=models.IntegerField(null=True,blank=True,db_index=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
      return str(self.order_id)

    
  
class EmailVerfication(models.Model):
      email = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
      is_verify=models.BooleanField(default=False)
  


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,db_index=True)
    course= models.ForeignKey(Course, on_delete=models.CASCADE,db_index=True,null=True)
    certificate_image = models.FileField(upload_to='certificates/',db_index=True,null=True)
    completion_date = models.DateTimeField(auto_now_add=True,db_index=True)

    # def _str_(self):
    #     return f"{self.user.username}'s Certificate for {self.bootcamp.name}"
  




class Teach(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    email = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    mobile = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    certification = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    qualification = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    message = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
      return str(self.name)