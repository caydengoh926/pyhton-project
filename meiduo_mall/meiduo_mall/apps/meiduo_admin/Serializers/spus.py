from rest_framework import serializers

from goods.models import SPU, Brand, GoodsCategory


class SpuSerializers(serializers.ModelSerializer):

    category1_id= serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    brand_id = serializers.IntegerField()
    brand = serializers.StringRelatedField(read_only=True)

    class Meta:
        model=SPU
        # fields='__all__'
        exclude = ('category1', 'category2', 'category3')


class BrandSerializers(serializers.ModelSerializer):

    class Meta:
        model=Brand
        fields='__all__'


class GoodsCategorySerializers(serializers.ModelSerializer):

    class Meta:
        model=GoodsCategory
        fields='__all__'



