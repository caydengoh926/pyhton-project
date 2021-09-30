from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Permission, ContentType
from rest_framework.permissions import IsAdminUser

from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.permissions import PermissionsSerializers, ContactTypeSerializers


class PermissionsView(ModelViewSet):

    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def contact_type(self, request):

        data = ContentType.objects.all()

        ser = ContactTypeSerializers(data, many=True)

        return Response(ser.data)