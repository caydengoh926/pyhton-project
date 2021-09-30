from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import IsAdminUser

from meiduo_admin.Serializers.permissions import PermissionsSerializers
from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.group import GroupSerializers


class GroupView(ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def simple(self, request):

        data = Permission.objects.all()

        ser = PermissionsSerializers(data, many=True)

        return Response(ser.data)