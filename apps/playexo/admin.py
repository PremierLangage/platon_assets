from django.contrib import admin

from playexo.models import Answer, PL



@admin.register(PL)
class PlAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')



@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'grade', 'get_pl_id', 'get_pl_name')
    
    
    def get_pl_name(self, obj):
        return obj.session.pl.name
    
    
    def get_pl_id(self, obj):
        return obj.session.pl.id
