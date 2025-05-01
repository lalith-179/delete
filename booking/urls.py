from . import views
from django.contrib import admin
from django.urls import path, include

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='mainpage'), 
    path('detail/<id>', views.movie_detail, name="movie detail"), 
    path('show', views.show_select, name="show select"),
    path('bookedseats', views.bookedseats, name="bookedseats"),
    path('mybookings', views.userbookings, name="mybookings"),
    path('checkout', views.checkout, name="checkout"), 
    path('cancelbooking/<int:id>', views.cancelbooking, name='cancel-booking'),
    path('payment/success/', views.payment_success, name='payment-success'),
    path('create-order/', views.create_order, name='create-order'),
    path('ticket/<str:booking_code>/', views.ticket_details, name='ticket-details'),
    path('ticket/<str:booking_code>/download/', views.generate_ticket_pdf, name='download-ticket'),
    
]