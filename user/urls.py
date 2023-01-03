from django.urls import path
from . import views

urlpatterns =[
    path('',views.main,name = "main"),
    path('loginVarify',views.loginVarify,name = "loginVarify"),
    path('sendHandle',views.sendHandle,name = "sendHandle"),
    path('watermarkPage',views.watermarkPage,name = "watermarkPage"),
    path('watermarkMsgHandle',views.watermarkMsgHandle,name = "watermarkMsgHandle"),
    path('encryptedImgPage',views.encryptedImgPage,name = "encryptedImgPage"),
    path('encryptede_image_handle',views.encryptede_image_handle,name = "encryptede_image_handle"),
]