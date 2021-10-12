from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import Brand


class BrandsSerializers(serializers.ModelSerializer):

    class Meta:
        model=Brand
        fields='__all__'

    def create(self, validated_data):

        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request']
        file = self.context['request'].FILES.get('logo')

        res = client.upload_by_buffer(file.read())

        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'err': 'image upload failed'})

        img = Brand.objects.create(name=validated_data['name'], logo=res['Remote file_id'], first_letter=validated_data['first_letter'])

        # generate_static_sku_detail_html.delay(img.sku.id)
        return img

    def update(self, instance, validated_data):

        client = Fdfs_client(settings.FASTDFS_PATH)

        # self.context['request']
        file = self.context['request'].FILES.get('logo')

        res = client.upload_by_buffer(file.read())

        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'err': 'image edit failed'})

        instance.logo= res['Remote file_id']
        instance.name = validated_data['name']
        instance.first_letter = validated_data['first_letter']
        instance.save()
        # img = Brand.objects.create(name=instance['name'], logo=res['Remote file_id'],
        #                            first_letter=instance['first_letter'])

        # generate_static_sku_detail_html.delay(instance.sku.id)
        return instance