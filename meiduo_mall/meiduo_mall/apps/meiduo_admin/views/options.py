from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.options import OptionSerializers, SPUSpecificationSerializers


class OptionView(ModelViewSet):

    queryset = SpecificationOption.objects.all()
    serializer_class = OptionSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def simple(self, request):

        data = SPUSpecification.objects.all()

        ser = SPUSpecificationSerializers(data, many=True)

        return Response(ser.data)