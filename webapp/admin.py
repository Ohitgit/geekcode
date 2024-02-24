from django.contrib import admin
from .models import *
# Register your models here.
from django_summernote.admin import SummernoteModelAdmin
admin.site.register(Category)

admin.site.register(SubCategory)
admin.site.register(order)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Profile)
admin.site.register(EmailVerfication)
admin.site.register(Language)






class CourseAdmin(SummernoteModelAdmin):
    model = Course
    summernote_fields = ('content',)
    list_display = ('title',)


admin.site.register(Course,CourseAdmin)

