from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.Serializers.goodschannels import GoodsChannelSerializers, Channel_TypesSerializers, GoodsCategorySerializers
from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from meiduo_admin.utils import PageNum


class GoodsChannelView(ModelViewSet):

    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def channel_types(self, request):

        data = GoodsChannelGroup.objects.all()

        ser = Channel_TypesSerializers(data, many=True)

        return Response(ser.data)

    def categories(self, request):

        data = GoodsCategory.objects.filter(parent=None)

        ser = GoodsCategorySerializers(data, many=True)

        return Response(ser.data)