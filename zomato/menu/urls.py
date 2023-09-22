
from django.urls import path
from menu import views

urlpatterns = [
   path("",views.menu , name="menu"),
   path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
]
