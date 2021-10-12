from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.Serializers.brands import BrandsSerializers
from goods.models import Brand
from meiduo_admin.utils import PageNum


class BrandsView(ModelViewSet):

    queryset = Brand.objects.all()
    serializer_class = BrandsSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]