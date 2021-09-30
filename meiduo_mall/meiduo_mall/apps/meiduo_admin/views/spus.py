# -*- coding: utf-8 -*-
from fdfs_client.client import Fdfs_client
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.conf import settings

from meiduo_admin.utils import PageNum
from goods.models import SPU, Brand, GoodsCategory
from meiduo_admin.Serializers.spus import SpuSerializers, BrandSerializers, GoodsCategorySerializers


class SpuView(ModelViewSet):

    queryset = SPU.objects.all()
    serializer_class = SpuSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def brand(self, request):

        data = Brand.objects.all()

        ser = BrandSerializers(data, many=True)

        return Response(ser.data)

    def channel(self, request):

        data = GoodsCategory.objects.filter(parent=None)

        ser = GoodsCategorySerializers(data, many=True)

        return Response(ser.data)

    def channels(self,request, pk):

        data = GoodsCategory.objects.filter(parent_id=pk)

        ser = GoodsCategorySerializers(data, many=True)

        return Response(ser.data)

    def image(self, request):
        """
            保存图片
        :param request:
        :return:
        """
        # 1、获取图片数据
        data = request.FILES.get('image')
        # 验证图片数据
        if data is None:
            return Response(status=500)

        # 2、建立fastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)

        # 3、上传图片
        res = client.upload_by_buffer(data.read())

        # 4、判断上传状态
        if res['Status'] != 'Upload successed.':
            return Response({'error': '上传失败'}, status=501)

        # 5、获取上传的图片路径
        image_url = res['Remote file_id']

        # 6、结果返回
        return Response(
            {
                'img_url': settings.FDFS_URL + image_url
            },

            status=201
        )


# class SPUGoodsView(ModelViewSet):
#     """
#         SPU表
#     """
#     serializer_class = SpuSerializers
#     queryset = SPU.objects.all()
#     pagination_class = PageNum
#     permission_classes = [IsAdminUser]


