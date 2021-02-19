import json
from typing import Optional

from common.errors import RestError
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from rest_framework import generics, mixins, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CircleSerializer, CircleResourceSerializer
from .models import Circle


class CircleList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        id_parent = self.request.query_params.get('id_circle', None)
        parent = None
        
        if id_parent is not None:
            parent = Circle.objects.get(pk=id_parent)
        kwargs = json.loads(request.body)
        kwargs['parent'] = parent
        circle = Circle.objects.create(kwargs)
        if not circle:
            return Response(
            RestError('circle/not-found'),
            status=status.HTTP_400_BAD_REQUEST
        )
        serializer = CircleSerializer(circle)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CircleDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    """View that allow to retrieve the informations of a single user"""
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """update cirle"""
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """update resource of circle"""
        # TODO changement de file.
        return self.update(request, *args, **kwargs)


class CircleResourceDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """View that allow to retrieve the informations of a single user"""
    queryset = Circle.objects.all()
    serializer_class = CircleResourceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CircleResourceTree(generics.ListAPIView):
    """retrive all parents of a single Circle"""
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get_queryset(self):
        queryset = Circle.objects.all()
        tree_id = []
        id_circle = self.request.query_params.get('id_circle', None)
        
        if id_circle is not None:
            tree_id.append(id_circle)
            circle = Circle.objects.get(id=id_circle)
            while(circle and circle.parent):
                circle = circle.parent
                tree_id.append(circle.id)
            
        queryset = queryset.filter(circle__pk__in=tree_id)
        return queryset 
