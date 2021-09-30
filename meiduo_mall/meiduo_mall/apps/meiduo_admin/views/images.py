from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import SKUImage, SKU
from meiduo_admin.utils import PageNum
from meiduo_admin.Serializers.images import ImagesSerializer, SKUSerializer


class ImagesView(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = ImagesSerializer

    pagination_class = PageNum

    permission_classes = [IsAdminUser]

    def simple(self, request):

        skus = SKU.objects.all()

        ser = SKUSerializer(skus, many=True)

        return Response(ser.data)

    # def create(self, request, *args, **kwargs):
    #
    #     data = request.data
    #
    #     ser = self.get_serializer(data = data)
    #
    #     ser.is_valid()
    #
    #     client = Fdfs_client(settings.FASTDFS_PATH)
    #
    #     file = request.FILES.get('image')
    #
    #     res = client.upload_by_buffer(file.read())
    #
    #     if res['Status'] != 'Upload successed.':
    #         return Response({'err': 'image upload failed'})
    #
    #     img = SKUImage.objects.create(sku = ser.validated_data['sku'], image = res['Remote file_id'])
    #     ser.save()
    #     return Response({
    #         'id': img.id,
    #         'sku':img.sku_id,
    #         'image':img.image.url
    #     })






