from django.core.files.base import ContentFile
from django.db import models
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db.models import Model
from django.contrib.auth.models import User
from rest_framework import serializers


from .ressources_storage import RessourceStorage



class Resource(models.Model):
    """Resource yep"""
    name = models.CharField(max_length=30, blank=True)
    path = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=150, blank=True)
    


class Circle(Resource):
    """Represents a unique circle"""
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)


    @classmethod
    async def create_circle(cls, path, name, id_parent=None):

        # TODO checker chaque user dans users, et le récupérer grâce à son id
        parent = None
        if id_parent:
            try:
                parent = await database_sync_to_async(cls.objects.get)(id=id_parent)
            except Circle.DoesNotExist:
                raise Circle.DoesNotExist
            except Circle.MultipleObjectsReturned:
                raise Circle.MultipleObjectsReturned
            
        return await database_sync_to_async(cls.objects.create)(name=name, parent=parent)



class File(models.Model):
    resource = models.ForeignKey(
        Resource,
        null=True,
        on_delete=models.CASCADE,
        related_name='files')
    document = models.FileField(storage=RessourceStorage())

    
    @classmethod
    async def create_file(cls, id_resource, filename, content):
        # TODO exeption when create
        try:
            resource = await database_sync_to_async(cls.objects.get)(id=id_resource)
        except Resource.DoesNotExist:
            raise Resource.DoesNotExist
        except Resource.MultipleObjectsReturned:
            raise Resource.MultipleObjectsReturned
        
        new_file = await database_sync_to_async(
            cls.objects.create)(resource=resource, document=None)
        new_file.document.save(filename, ContentFile(content))


    @classmethod
    async def update_file(cls, id_file: int, content: str):
        # TODO create file in specific folders
        try:
            r = await database_sync_to_async(cls.objects.get)(id=id_file)
        except cls.DoesNotExist:
            return
        with r.resource.open("w+") as f:
            f.write(content)
    

    def __str__(self):
        return '%s: %s' % (self.document.name, self.document.path)
