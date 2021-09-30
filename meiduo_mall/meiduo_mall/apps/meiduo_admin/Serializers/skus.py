from rest_framework import serializers
from django.db import transaction

from goods.models import SKU, GoodsCategory, SpecificationOption, SPUSpecification, SKUSpecification
from celery_tasks.static_file.tasks import generate_static_sku_detail_html


class SKUSpecificationSerializers(serializers.ModelSerializer):

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model=SKUSpecification
        fields=('spec_id', 'option_id')


class SKUSerializers(serializers.ModelSerializer):

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    specs = SKUSpecificationSerializers(read_only=True, many=True)

    class Meta:
        model=SKU
        fields='__all__'
        read_only_fields=('spu', 'category')

    def create(self, validated_data):
        specs = self.context['request'].data.get('specs')

        with transaction.atomic():
            save_point = transaction.savepoint()

            try:
                sku = SKU.objects.create(**validated_data)

                for spec in specs:
                    SKUSpecification.objects.create(spec_id=spec['spec_id'], option_id=spec['option_id'], sku=sku)

            except:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('save data failed')

            else:
                transaction.savepoint_commit(save_point)

                generate_static_sku_detail_html.delay(sku.id)

                return sku

    def update(self, instance, validated_data):
        specs = self.context['request'].data.get('specs')

        with transaction.atomic():
            save_point = transaction.savepoint()

            try:
                SKU.objects.filter(id = instance.id).update(**validated_data)

                for spec in specs:
                    SKUSpecification.objects.filter(sku = instance).update(**spec)

            except:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('edit data failed')

            else:
                transaction.savepoint_commit(save_point)

                generate_static_sku_detail_html.delay(instance.id)

                return instance


class GoodsCategorySerializers(serializers.ModelSerializer):

    class Meta:
        model=GoodsCategory
        fields='__all__'

class SpecificationOptionSerializers(serializers.ModelSerializer):

    class Meta:
        model=SpecificationOption
        fields='__all__'


class SPUSpecificationSerializers(serializers.ModelSerializer):

    options= SpecificationOptionSerializers(many=True)
    class Meta:
        model=SPUSpecification
        fields='__all__'