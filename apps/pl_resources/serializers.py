from .models import Circle
from rest_framework import serializers


class CircleResourceSerializer(serializers.ModelSerializer):
    
    files = serializers.StringRelatedField(many=True)

    class Meta:
        model = Circle
        fields = ('id', 'name', 'path', 'description', 'files')


class CircleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Circle
        fields = ('id', 'name', 'path', 'description')
