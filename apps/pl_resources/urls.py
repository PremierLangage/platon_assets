from django.urls import path, include

from . import views

app_name = 'pl_resources'

urlpatterns = [
    path('circles/', views.CircleList.as_view(), name='circle-list'),
    path('circle/', views.CircleDetail.as_view(), name='circle-detail'),
    path('circle/resources/', views.CircleResourceDetail.as_view(), name='circle-resources-detail'),
    path('circle/tree/', views.CircleResourceTree.as_view(), name='circle-resources-tree'),
]
