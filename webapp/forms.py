from django import forms

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
class SignupForm(forms.Form):
    first = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=15)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    checkbox = forms.BooleanField(required=False)

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))




class TeachForm(forms.Form):
   
    name=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Name'}))
    email=forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    certification=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Certification'}))
    qualification=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Qualification'}))
    message=forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Message'}))
    captcha = ReCaptchaField(widget=ReCaptchaV3)