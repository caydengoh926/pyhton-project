from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers
from rest_framework.response import Response

from goods.models import SKUImage, SKU
from celery_tasks.static_file.tasks import generate_static_sku_detail_html


class ImagesSerializer(serializers.ModelSerializer):

    # sku_id = serializers.IntegerField()
    class Meta:
        model= SKUImage
        fields= '__all__'

    def create(self, validated_data):

        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request']
        file = self.context['request'].FILES.get('image')

        res = client.upload_by_buffer(file.read())

        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'err': 'image upload failed'})

        img = SKUImage.objects.create(sku=validated_data['sku'], image=res['Remote file_id'])

        generate_static_sku_detail_html.delay(img.sku.id)
        return img

    def update(self, instance, validated_data):

        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request']
        file = self.context['request'].FILES.get('image')

        res = client.upload_by_buffer(file.read())

        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'err': 'image edit failed'})

        instance.image= res['Remote file_id']
        instance.save()

        generate_static_sku_detail_html.delay(instance.sku.id)
        return instance


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model=SKU
        fields= ('id', 'name')