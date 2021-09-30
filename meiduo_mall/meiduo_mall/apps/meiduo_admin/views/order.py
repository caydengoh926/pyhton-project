from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from meiduo_admin.utils import PageNum
from orders.models import OrderInfo
from meiduo_admin.Serializers.order import OrderSerializers


class OrderView(ReadOnlyModelViewSet):

    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializers
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return OrderInfo.objects.all()
        elif self.request.query_params.get('keyword') is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains= self.request.query_params.get('keyword'))

    @action(methods=['put'], detail=True)
    def status(self, request, pk):

        try:
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'err':'order id incorrect'})

        status=request.data.get('status')
        if status is None:
            return Response({'err': 'status empty'})
        order.status = status
        order.save()

        return Response({
            'order_id': pk,
            'status':status
        })

