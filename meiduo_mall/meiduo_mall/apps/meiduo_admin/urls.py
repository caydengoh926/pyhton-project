from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from views import statistical, eusers
from .views import specs, images, skus, order, permissions, group, admin, spus, options, goodschannels, brands

urlpatterns = [
    # url(r'^', admin.site.urls),

    url(r'^authorizations/$', obtain_jwt_token),

    url(r'^statistical/total_count/$', statistical.UserCountView.as_view()),

    url(r'^statistical/day_increment/$', statistical.UserDayCountView.as_view()),

    url(r'^statistical/day_active/$', statistical.UserDayActiveCountView.as_view()),

    url(r'^statistical/day_orders/$', statistical.UserDayOrdersCountView.as_view()),

    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),

    url(r'^statistical/goods_day_views/$', statistical.UserGoodsCountView.as_view()),

    url(r'^users/$', eusers.UserView.as_view()),

    url(r'^goods/simple/$', specs.SpecsView.as_view({'get':'simple'})),

    url(r'^skus/simple/$', images.ImagesView.as_view({'get':'simple'})),

    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SKUVIew.as_view({'get':'specs'})),

    url(r'^permission/content_types/$', permissions.PermissionsView.as_view({'get':'contact_type'})),

    url(r'^permission/simple/$', group.GroupView.as_view({'get':'simple'})),

    url(r'^permission/groups/simple/$', admin.AdminView.as_view({'get':'simple'})),

    url(r'^goods/brands/simple/$', spus.SpuView.as_view({'get':'brand'})),

    url(r'^goods/channel/categories/$', spus.SpuView.as_view({'get':'channel'})),

    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spus.SpuView.as_view({'get':'channels'})),

    url(r'^goods/images/$', spus.SpuView.as_view({'post':'image'})),

    url(r'^goods/specs/simple/$', options.OptionView.as_view({'get':'simple'})),

    url(r'^goods/channel_types/$', goodschannels.GoodsChannelView.as_view({'get':'channel_types'})),

    url(r'^goods/categories/$', goodschannels.GoodsChannelView.as_view({'get':'categories'})),

]

router = DefaultRouter()
router.register('goods/brands', brands.BrandsView, base_name='brands')
print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('goods/channels', goodschannels.GoodsChannelView, base_name='channels')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, base_name='specs')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('skus/images', images.ImagesView, base_name='images')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('skus', skus.SKUVIew, base_name='skus')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('orders', order.OrderView, base_name='orders')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('permission/perms', permissions.PermissionsView, base_name='perms')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('permission/groups', group.GroupView, base_name='groups')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('permission/admins', admin.AdminView, base_name='admins')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('goods', spus.SpuView, base_name='goods')
# print(router.urls)
urlpatterns += router.urls

router = DefaultRouter()
router.register('specs/options', options.OptionView, base_name='options')
# print(router.urls)
urlpatterns += router.urls

