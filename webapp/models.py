from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

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
     
class Course(models.Model):
   
    
    slug = models.SlugField(max_length=255, unique=True, blank=True,null=True,db_index=True)
    title = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    author = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    rating = models.CharField(max_length=100,null=True,blank=True ,db_index=True)
    languge = models.ForeignKey(Language, on_delete=models.CASCADE,null=True,db_index=True)
    content=models.TextField(null=True)
    short_description=models.TextField(null=True)
    price = models.IntegerField(null=True,blank=True ,db_index=True)
    image=models.FileField(null=True,db_index=True,upload_to='media/images/')
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
      return str(self.title)

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
   