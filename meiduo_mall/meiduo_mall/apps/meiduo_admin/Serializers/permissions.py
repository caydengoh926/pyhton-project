from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType

class PermissionsSerializers(serializers.ModelSerializer):

    class Meta:
        model= Permission
        fields = '__all__'


class ContactTypeSerializers(serializers.ModelSerializer):

    name = serializers.CharField()

    class Meta:
        model= ContentType
        fields = '__all__'