from django.contrib import admin
from .models import UserInformation,UserAccountBalance

# Register your models here.
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ("username","accountNumber")

class UserAccountBalanceAdmin(admin.ModelAdmin):
    list_display = ("accountNumber","balance")

admin.site.register(UserInformation,UserInformationAdmin)
admin.site.register(UserAccountBalance,UserAccountBalanceAdmin)