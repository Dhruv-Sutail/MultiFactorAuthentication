from django.contrib import admin
from .models import UserInformation

# Register your models here.
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ("username","accountNumber")


admin.site.register(UserInformation,UserInformationAdmin)