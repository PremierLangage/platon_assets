from django.urls import path

from playexo import views


app_name = 'playexo'

urlpatterns = [
    path(r'pl/<int:pl_id>/', views.get_pl, name="get_pl"),
    path(r'pl/', views.post_pl, name="post_pl"),
    path(r'evaluate/<int:pl_id>/', views.evaluate_pl, name="evaluate_pl"),
    path(r'reroll/<int:pl_id>', views.reroll, name="reroll_pl")
]
