from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from .models import UserInformation,UserAccountBalance
import boto3
import random
import string
import requests
from datetime import date,timedelta

today = date.today()
yesterday = today - timedelta(days = 2)

queue_url = 'https://sqs.ap-south-1.amazonaws.com/499607506705/MFA_AccountNumber'
stock_url = ['https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TATACHEM.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ADANIENT.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ONGC.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TITAN.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K']
crypto_url = ['https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=ETH&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=THETA&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=DOT&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BNB&market=USD&apikey=BVL5MGAAMSINNX3K']

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
        context = {}
        if UserInformation.objects.filter(username=name).exists(): 
            context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
            context["date"] = today.strftime("%b %d %Y")
            if UserAccountBalance.objects.filter(username=name).exists():
                context["accountbalance"] = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                return render(request , "Profile.html",context)
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

class FixedDepositView(View):
    def get(self , request):
        context = {}
        name = request.user
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        context["date"] = today.strftime("%b %d %Y")
        return render(request,"FixedDeposit.html",context)

class AddMoneyView(View):
    def get(self,request):
        context = {}
        name = request.user
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        context["date"] = today.strftime("%b %d %Y")
        if UserAccountBalance.objects.filter(username=name).exists():
            context["accountbalance"] = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
        return render(request,"AddMoney.html",context)
    
    def post(self,request):
        name = request.user
        if UserAccountBalance.objects.filter(username=name).exists():
            oldbalance = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
            balance = request.POST['amount']
            newbalance = int(oldbalance) + int(balance)
            print(newbalance)
            totalbalance = UserAccountBalance.objects.filter(username=name).update(balance=newbalance)
            return HttpResponseRedirect(reverse("addmoney"))
        else:
            if request.method == "POST":
                accountNumber = request.POST['accountnumber']
                Accountnumber = UserInformation.objects.get(accountNumber=accountNumber)
                balance = request.POST['amount']
                userbalance = UserAccountBalance(
                    username = name,
                    accountNumber = Accountnumber,
                    balance = balance,
                )
                userbalance.save()
                return HttpResponseRedirect(reverse("addmoney"))

class StocksView(View):
    def get(self , request):
        context = {}
        name = request.user
        stock = []
        price = []
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        for i in range(len(stock_url)):
            r = requests.get(stock_url[i])
            data = r.json()
            stock.append(data['Meta Data']['2. Symbol'])
            price.append(data["Time Series (Daily)"][str(yesterday)]["4. close"])
        context["stock"] = stock
        context["price"] = price   
        context["date"] = today.strftime("%b %d %Y")
        return render(request,"Stocks.html",context)

class CryptoCurrencyView(View):
    def get(self , request):
        context = {}
        name = request.user
        crypto = []
        price = []
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        for i in range(len(crypto_url)):
            r = requests.get(crypto_url[i])
            data = r.json()
            crypto.append(data['Meta Data']['3. Digital Currency Name'])
            price.append(int(float(data['Time Series (Digital Currency Daily)'][str(yesterday)]["4b. close (USD)"]))*75.08)
        context["crypto"] = crypto
        context["price"] = price
        context["date"] = today.strftime("%b %d %Y")
        return render(request,"CryptoCurrency.html",context)

class LogoutView(View):
    def post(self, request):
        if request.method == "POST":
            logout(request)
            return HttpResponseRedirect(reverse("login"))