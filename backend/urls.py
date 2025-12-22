"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views as core_views
from core.views_home import index_view, products_view
from django.urls import include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index_view, name='home'),
    path('products/', products_view, name='products'),
    path('portal/login/', core_views.staff_login, name='staff-login'),
    path('portal/logout/', core_views.staff_logout, name='staff-logout'),
    path('portal/students/', core_views.admin_students_page, name='admin-students-page'),
    path('portal/courses/', core_views.admin_courses_page, name='admin-courses-page'),
    path('admin/', admin.site.urls),
    path('api/register/', core_views.register_view, name='api-register'),
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
