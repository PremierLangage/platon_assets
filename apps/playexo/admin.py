from django.contrib import admin

from playexo.models import PL



@admin.register(PL)
class PlAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
