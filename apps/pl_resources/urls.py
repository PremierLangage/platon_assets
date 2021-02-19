from django.urls import path, include

from . import views

app_name = 'pl_resources'

urlpatterns = [
    path('api/circles/', views.CircleList.as_view(), name='circle-list'),
    path('api/circle/', views.CircleDetail.as_view(), name='circle-detail'),
    path('api/circle/resources/', views.CircleResourceDetail.as_view(), name='circle-resources-detail'),
    path('api/circle/tree/', views.CircleResourceTree.as_view(), name='circle-resources-tree'),
]
