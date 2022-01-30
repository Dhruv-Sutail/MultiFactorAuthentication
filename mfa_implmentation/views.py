from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from .models import UserInformation
import boto3
import random
import string

queue_url = 'https://sqs.ap-south-1.amazonaws.com/499607506705/MFA_AccountNumber'

def getAuthenticateEmail(email):
	sqs = boto3.client('sqs',region_name='ap-south-1')
	
	# Send message to SQS queue
	response = sqs.send_message(
		QueueUrl=queue_url,
		DelaySeconds=10,
		MessageAttributes={
			'email': {
				'DataType': 'String',
				'StringValue': email
			},
			'is_secret': {
				'DataType': 'String',
				'StringValue': "no"
			}					
		},
		MessageBody=(
			'sgnons'
		)
	)
	print("\n\n\n\n\n")
	print(response['MessageId'])


def callSQS(Secret,email):
	sqs = boto3.client('sqs',region_name='ap-south-1')

	response = sqs.send_message(
		QueueUrl=queue_url,
		DelaySeconds=10,
		MessageAttributes={
			'Secret': {
				'DataType': 'String',
				'StringValue': Secret
			},
			'email': {
				'DataType': 'String',
				'StringValue': email
			},
			'is_secret': {
				'DataType': 'String',
				'StringValue': "yes"
			}		
		},
		MessageBody=(
			'sgnons'
		)
	)

	print(response['MessageId'])

def GetSecret():
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 11))

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
                getAuthenticateEmail(email)
                context["success"] = "You have Registered Successfully! Please Check Your Email for Authentication:)"
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
        context = {}
        if request.method == "POST":
            user = request.user
            print(user)
            Account = GetSecret()
            email = User.objects.filter(username=user).values_list('email', flat=True)[0]
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
            callSQS(Account,email)
            context["success"] = "Please Verify Your Account Number with the Email also!"
            return HttpResponseRedirect(reverse("profile"))

class LogoutView(View):
    def post(self, request):
        if request.method == "POST":
            logout(request)
            return HttpResponseRedirect(reverse("login"))