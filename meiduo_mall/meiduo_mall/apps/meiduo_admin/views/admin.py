from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group

from meiduo_admin.utils import PageNum
from users.models import User
from meiduo_admin.Serializers.admin import AdminSerializers
from meiduo_admin.Serializers.group import GroupSerializers


class AdminView(ModelViewSet):

    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def simple(self, request):

        data = Group.objects.all()

        ser = GroupSerializers(data, many=True)

        return Response(ser.data)