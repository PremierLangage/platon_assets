from .models import Circle
from rest_framework import serializers


class CircleSerializer(serializers.ModelSerializer):
    
    files = serializers.StringRelatedField(many=True)

    class Meta:
        Model = Circle
        fields = ['name', 'path', 'description', 'files']
