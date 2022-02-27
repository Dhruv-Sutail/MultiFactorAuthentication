from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    path('',views.HomeView.as_view(),name="home"),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('user-profile/',views.LoginSuccessView.as_view(),name="profile"),
    path('user-profile/FixedDeposit',views.FixedDepositView.as_view(),name="fixeddeposit"),
    path('user-profile/AddMoney',views.AddMoneyView.as_view(),name="addmoney"),
    path('user-profile/Stocks',views.StocksView.as_view(),name="stocks"),
    path('user-profile/CryptoCurrency', views.CryptoCurrencyView.as_view(),name="cryptocurrency"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
]