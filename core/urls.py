from django.urls import path
from . import views

urlpatterns = [
    path('admin/registrations/', views.registrations_list, name='admin-registrations-list'),
    path('admin/registrations/<int:pk>/', views.registration_detail, name='admin-registrations-detail'),
    path('admin/registrations/<int:pk>/download/', views.download_proof, name='admin-registrations-download'),
]
