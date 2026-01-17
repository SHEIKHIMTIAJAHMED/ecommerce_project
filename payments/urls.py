from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:order_id>/', views.checkout, name='payment_checkout'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
]