# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-08-14 07:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=20, verbose_name='\u540d\u79f0')),
                ('logo', models.ImageField(upload_to=b'', verbose_name='Logo\u56fe\u7247')),
                ('first_letter', models.CharField(max_length=1, verbose_name='\u54c1\u724c\u9996\u5b57\u6bcd')),
            ],
            options={
                'db_table': 'tb_brand',
                'verbose_name': '\u54c1\u724c',
                'verbose_name_plural': '\u54c1\u724c',
            },
        ),
        migrations.CreateModel(
            name='GoodsCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=10, verbose_name='\u540d\u79f0')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subs', to='goods.GoodsCategory', verbose_name='\u7236\u7c7b\u522b')),
            ],
            options={
                'db_table': 'tb_goods_category',
                'verbose_name': '\u5546\u54c1\u7c7b\u522b',
                'verbose_name_plural': '\u5546\u54c1\u7c7b\u522b',
            },
        ),
        migrations.CreateModel(
            name='GoodsChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('url', models.CharField(max_length=50, verbose_name='\u9891\u9053\u9875\u9762\u94fe\u63a5')),
                ('sequence', models.IntegerField(verbose_name='\u7ec4\u5185\u987a\u5e8f')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.GoodsCategory', verbose_name='\u9876\u7ea7\u5546\u54c1\u7c7b\u522b')),
            ],
            options={
                'db_table': 'tb_goods_channel',
                'verbose_name': '\u5546\u54c1\u9891\u9053',
                'verbose_name_plural': '\u5546\u54c1\u9891\u9053',
            },
        ),
        migrations.CreateModel(
            name='GoodsChannelGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=20, verbose_name='\u9891\u9053\u7ec4\u540d')),
            ],
            options={
                'db_table': 'tb_channel_group',
                'verbose_name': '\u5546\u54c1\u9891\u9053\u7ec4',
                'verbose_name_plural': '\u5546\u54c1\u9891\u9053\u7ec4',
            },
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=50, verbose_name='\u540d\u79f0')),
                ('caption', models.CharField(max_length=100, verbose_name='\u526f\u6807\u9898')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='\u5355\u4ef7')),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='\u8fdb\u4ef7')),
                ('market_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='\u5e02\u573a\u4ef7')),
                ('stock', models.IntegerField(default=0, verbose_name='\u5e93\u5b58')),
                ('sales', models.IntegerField(default=0, verbose_name='\u9500\u91cf')),
                ('comments', models.IntegerField(default=0, verbose_name='\u8bc4\u4ef7\u6570')),
                ('is_launched', models.BooleanField(default=True, verbose_name='\u662f\u5426\u4e0a\u67b6\u9500\u552e')),
                ('default_image_url', models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='\u9ed8\u8ba4\u56fe\u7247')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.GoodsCategory', verbose_name='\u4ece\u5c5e\u7c7b\u522b')),
            ],
            options={
                'db_table': 'tb_sku',
                'verbose_name': '\u5546\u54c1SKU',
                'verbose_name_plural': '\u5546\u54c1SKU',
            },
        ),
        migrations.CreateModel(
            name='SKUImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('image', models.ImageField(upload_to=b'', verbose_name='\u56fe\u7247')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.SKU', verbose_name='sku')),
            ],
            options={
                'db_table': 'tb_sku_image',
                'verbose_name': 'SKU\u56fe\u7247',
                'verbose_name_plural': 'SKU\u56fe\u7247',
            },
        ),
        migrations.CreateModel(
            name='SKUSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'db_table': 'tb_sku_specification',
                'verbose_name': 'SKU\u89c4\u683c',
                'verbose_name_plural': 'SKU\u89c4\u683c',
            },
        ),
        migrations.CreateModel(
            name='SpecificationOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('value', models.CharField(max_length=20, verbose_name='\u9009\u9879\u503c')),
            ],
            options={
                'db_table': 'tb_specification_option',
                'verbose_name': '\u89c4\u683c\u9009\u9879',
                'verbose_name_plural': '\u89c4\u683c\u9009\u9879',
            },
        ),
        migrations.CreateModel(
            name='SPU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=50, verbose_name='\u540d\u79f0')),
                ('sales', models.IntegerField(default=0, verbose_name='\u9500\u91cf')),
                ('comments', models.IntegerField(default=0, verbose_name='\u8bc4\u4ef7\u6570')),
                ('desc_detail', models.TextField(default='', verbose_name='\u8be6\u7ec6\u4ecb\u7ecd')),
                ('desc_pack', models.TextField(default='', verbose_name='\u5305\u88c5\u4fe1\u606f')),
                ('desc_service', models.TextField(default='', verbose_name='\u552e\u540e\u670d\u52a1')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.Brand', verbose_name='\u54c1\u724c')),
                ('category1', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cat1_spu', to='goods.GoodsCategory', verbose_name='\u4e00\u7ea7\u7c7b\u522b')),
                ('category2', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cat2_spu', to='goods.GoodsCategory', verbose_name='\u4e8c\u7ea7\u7c7b\u522b')),
                ('category3', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cat3_spu', to='goods.GoodsCategory', verbose_name='\u4e09\u7ea7\u7c7b\u522b')),
            ],
            options={
                'db_table': 'tb_spu',
                'verbose_name': '\u5546\u54c1SPU',
                'verbose_name_plural': '\u5546\u54c1SPU',
            },
        ),
        migrations.CreateModel(
            name='SPUSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4')),
                ('name', models.CharField(max_length=20, verbose_name='\u89c4\u683c\u540d\u79f0')),
                ('spu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SPU', verbose_name='\u5546\u54c1SPU')),
            ],
            options={
                'db_table': 'tb_spu_specification',
                'verbose_name': '\u5546\u54c1SPU\u89c4\u683c',
                'verbose_name_plural': '\u5546\u54c1SPU\u89c4\u683c',
            },
        ),
        migrations.AddField(
            model_name='specificationoption',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='goods.SPUSpecification', verbose_name='\u89c4\u683c'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.SpecificationOption', verbose_name='\u89c4\u683c\u503c'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='sku',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specs', to='goods.SKU', verbose_name='sku'),
        ),
        migrations.AddField(
            model_name='skuspecification',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='goods.SPUSpecification', verbose_name='\u89c4\u683c\u540d\u79f0'),
        ),
        migrations.AddField(
            model_name='sku',
            name='spu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.SPU', verbose_name='\u5546\u54c1'),
        ),
        migrations.AddField(
            model_name='goodschannel',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.GoodsChannelGroup', verbose_name='\u9891\u9053\u7ec4\u540d'),
        ),
    ]