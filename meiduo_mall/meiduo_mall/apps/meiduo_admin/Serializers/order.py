from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUSerializers(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializers(serializers.ModelSerializer):

    sku = SKUSerializers()

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderSerializers(serializers.ModelSerializer):

    skus=OrderGoodsSerializers(many=True)

    class Meta:
        model=OrderInfo
        fields='__all__'