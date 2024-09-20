from django.urls import path
from . import views

urlpatterns = [
    path('lists/', views.lists), # [POST] create list
    path('lists/join/', views.join), # [POST] add listuser given code (and user) if matching a sharecode
    path('lists/<int:list_id>/', views.list), # [GET, DELETE] get, delete list
    path('lists/<int:list_id>/share/', views.share), # [POST] create share code for username
    path('lists/<int:list_id>/items/', views.items), # [POST] add item
    path('lists/<int:list_id>/items/<int:item_id>/', views.item), # [PATCH,DELETE] delete, update item
]
