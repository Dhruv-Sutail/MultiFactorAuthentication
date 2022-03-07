from django.contrib import admin
from .models import UserInformation,UserAccountBalance,UserMfaSecret

# Register your models here.
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ("username","accountNumber")

class UserAccountBalanceAdmin(admin.ModelAdmin):
    list_display = ("accountNumber","balance")

class UserMfaSecretAdmin(admin.ModelAdmin):
    list_display = ("username","secret")

admin.site.register(UserInformation,UserInformationAdmin)
admin.site.register(UserAccountBalance,UserAccountBalanceAdmin)