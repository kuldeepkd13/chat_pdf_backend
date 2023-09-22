
from django.urls import path
from menu import views

urlpatterns = [
   path("",views.menu , name="menu"),
   path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
   path('upload/', views.pdf_upload_view, name='upload'),
   path('chat/', views.chat_view, name='chat'),
   path('endchat/', views.end_chat_view, name='endchat'),
]
