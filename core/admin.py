from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'course', 'auto_bridge', 'created_at')
    list_filter = ('auto_bridge', 'created_at')
    search_fields = ('name', 'email', 'contact', 'course')
from django.contrib import admin

# Register your models here.
