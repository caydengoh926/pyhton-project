from rest_framework import serializers
from goods.models import GoodsVisitCount


class UserGoodsCountSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')