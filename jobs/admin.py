from django.contrib import admin

# Register your models here.

from .models import Job


class JobsAdmin(admin.ModelAdmin):
    list_display=('name','description','created_at','updated_at','is_archived','created_by')
    list_filter=('created_at','updated_at','is_archived','created_by')
    search_fields=('name','description','created_at','updated_at','is_archived','created_by')

admin.site.register(Job, JobsAdmin)
