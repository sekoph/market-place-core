from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name', 'email', 'phone', 'username', 'created_at', 'updated_at']
    search_fields = ['username']