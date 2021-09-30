from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta

from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.Serializers.statistical import UserGoodsCountSerializer


class UserCountView(APIView):

    permission_classes = [IsAdminUser]
    def get(self, request):

        now_date = date.today()

        count = User.objects.all().count()

        return Response({

            'date' : now_date,
            'count' : count
        })

class UserDayCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        count = User.objects.filter(date_joined__gte=now_date).count()

        return Response({

            'date': now_date,
            'count': count
        })


class UserDayActiveCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        count = User.objects.filter(last_login__gte=now_date).count()

        return Response({

            'date': now_date,
            'count': count
        })


class UserDayOrdersCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        count = len(set(User.objects.filter(orderinfo__create_time__gte=now_date)))

        return Response({

            'date': now_date,
            'count': count
        })


class UserMonthCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        begin_date = now_date - timedelta(days=29)

        data_list=[]
        for i in range(30):

            index_date = begin_date + timedelta(days=i)

            next_date = begin_date + timedelta(days=i+1)

            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date).count()

            data_list.append({
                'count': count,
                'date':index_date
            })

        return Response(data_list)


class UserGoodsCountView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()

        goods = GoodsVisitCount.objects.filter(date__gte= now_date)

        ser = UserGoodsCountSerializer(goods, many=True)

        return Response(ser.data)
