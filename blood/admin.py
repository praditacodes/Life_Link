from django.contrib import admin
from .models import CustomUser, Stock, BloodRequest

class CustomUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CustomUser._meta.fields]
    search_fields = [field.name for field in CustomUser._meta.fields]
    list_filter = [field.name for field in CustomUser._meta.fields if field.get_internal_type() in ['BooleanField', 'CharField']]

class StockAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Stock._meta.fields]
    search_fields = [field.name for field in Stock._meta.fields]

class BloodRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BloodRequest._meta.fields]
    search_fields = [field.name for field in BloodRequest._meta.fields]
    list_filter = [field.name for field in BloodRequest._meta.fields if field.get_internal_type() in ['CharField', 'DateField']]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(BloodRequest, BloodRequestAdmin)
