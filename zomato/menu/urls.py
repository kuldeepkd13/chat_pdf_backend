
from django.urls import path
from menu import views

urlpatterns = [
   path("",views.menu , name="menu"),
   path('create' , views.create , name = "create"),
   path('view' , views.view , name='view'),
   path('update/<int:dish_id>/', views.update_availability, name='update_availability'),
   path('delete/<int:dish_id>/', views.delete_dish, name='delete_dish'),
   path('order/create/', views.create_order, name='create_order'),
   path('view/<int:dish_id>/', views.view_dish, name='view_dish'),
   path('order/view', views.get_orders, name='get_orders'),
   path('update/orderstatus/<int:order_id>/', views.update_order_status, name='update_order_status')
]
