from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SKU, GoodsCategory, SPU
from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.skus import SKUSerializers, GoodsCategorySerializers, SPUSpecificationSerializers


class SKUVIew(ModelViewSet):

    queryset = SKU.objects.all()

    serializer_class = SKUSerializers

    pagination_class = PageNum

    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return SKU.objects.all()
        elif self.request.query_params.get('keyword') is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains= self.request.query_params.get('keyword'))

    @action(methods=['get'], detail=False)
    def categories(self, request):

        data = GoodsCategory.objects.filter(subs__id = None)

        ser = GoodsCategorySerializers(data, many=True)

        return Response(ser.data)

    def specs(self, request, pk):

        spu = SPU.objects.get(id= pk)

        data = spu.specs.all()

        ser = SPUSpecificationSerializers(data, many=True)

        return Response(ser.data)