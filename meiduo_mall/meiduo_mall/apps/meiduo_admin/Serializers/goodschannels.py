from rest_framework import serializers

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


class GoodsChannelSerializers(serializers.ModelSerializer):

    group = serializers.CharField(read_only=True)
    group_id = serializers.IntegerField()
    category = serializers.CharField(read_only=True)
    category_id = serializers.IntegerField()

    class Meta:
        model=GoodsChannel
        fields='__all__'


class Channel_TypesSerializers(serializers.ModelSerializer):

    class Meta:
        model=GoodsChannelGroup
        fields='__all__'


class GoodsCategorySerializers(serializers.ModelSerializer):

    class Meta:
        model=GoodsCategory
        fields='__all__'