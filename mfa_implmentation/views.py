from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from .models import UserInformation



class HomeView(View):
    def get(self , request):
        return render(request,"Homepage/Home.html")

class RegisterView(View):
    def get(self , request):
        return render(request,"Register.html")
    
    def post(self, request):
        context = {}
        if request.method == "POST":
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']    
            confirm_password = request.POST['confirm_password']
            if(password==confirm_password):
                userprofile = User(
                    username = username,
                    email = email,
                    password = make_password(password)
                )
                userprofile.save()
                context["success"] = "You have Registered Successfully! Please Login Now:)"
                return render(request, "Register.html",context)
            else:
                context["error"] = "Please Enter Same password and Confirm password!!"
                return render(request, "Register.html",context)
        else:
            context["error"] = "Some Error Occured Please Try Again:("
            return render(request, "Register.html",context)

class LoginView(View):
    def get(self , request):
        return render(request,"Login.html")

    def post(self , request):
        context = {}
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            print(username)
            user = authenticate(request,username=username,password=password)
            if user:
                login(request,user)
                request.session['username'] = user.username
                return HttpResponseRedirect(reverse("profile"))
            else:
                context["error"] = "Enter Valid Credentials!!"
                return render(request , "Login.html",context)

class LoginSuccessView(View):
    def get(self , request):
        name = request.user
        if UserInformation.objects.filter(username=name).exists():
            print(name)
            return render(request , "Profile.html")
        else:
            return render(request , "PersonalQuestions.html")
    
    def post(self,request):
        if request.method == "POST":
            user = request.user
            Account = 12345678901
            dish = request.POST['dish']
            middlename = request.POST['middlename']
            city = request.POST['city']
            userdetails = UserInformation(
                username = user,
                accountNumber = Account,
                favourite_dish = dish,
                middle_name = middlename,
                city = city 
            )
            userdetails.save()
            return HttpResponseRedirect(reverse("profile"))

class LogoutView(View):
    def post(self, request):
        if request.method == "POST":
            logout(request)
            return HttpResponseRedirect(reverse("login"))