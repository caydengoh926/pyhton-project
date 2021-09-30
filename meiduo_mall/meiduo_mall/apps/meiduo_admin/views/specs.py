from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from goods.models import SPUSpecification, SPU
from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.specs import SpecsSerializer, SPUSerializer


class SpecsView(ModelViewSet):

    queryset = SPUSpecification.objects.all()

    serializer_class = SpecsSerializer

    pagination_class = PageNum


    def simple(self, request):

        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)

        return Response(ser.data)