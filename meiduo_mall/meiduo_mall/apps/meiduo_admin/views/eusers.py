from rest_framework.generics import ListAPIView, ListCreateAPIView

from users.models import User
from meiduo_admin.Serializers.eusers import UserSerializer
from meiduo_admin.utils import PageNum


class UserView(ListCreateAPIView):

    # queryset = User.objects.all()

    serializer_class = UserSerializer

    pagination_class = PageNum

    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return User.objects.all()
        else:
            return User.objects.filter(username__contains= self.request.query_params.get('keyword'))

