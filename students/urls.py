from django.urls import path
from . import views

urlpatterns = [
    path('',           views.scanner_page, name='scanner'),
    path('api/verify/', views.verify_qr,   name='verify_qr'),
    path('api/stats/',  views.stats_view,  name='stats'),
]