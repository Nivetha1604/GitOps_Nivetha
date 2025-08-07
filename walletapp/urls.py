from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_home, name='landing_home'),   
    path('login/', views.login_user, name='login'), 
    path('upload_profile_picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('register/', views.show_register_form, name='show_register_form'),
    path('register_user/', views.register_user, name='register_user'),
    path('dashboard/', views.wallet_main, name='wallet_main'),
    path('add_funds/', views.add_funds, name='add_funds'),
    path('transfer/', views.transfer_money, name='transfer_money'),
    path('merchant/', views.merchant_payment, name='merchant_payment'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('settings/', views.settings_page, name='settings'),
    path('update_settings/', views.update_settings, name='update_settings'),
    path('logout/', views.logout_user, name='logout'),
]








