from rest_framework import serializers
import re

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields= ('id', 'username', 'mobile', 'email', 'password')
        extra_kwargs={
            'password':{
                'write_only':True,
                'max_length':20,
                'min_length':8
            },
            'username':{
                'max_length': 20,
                'min_length': 8
            }
        }

    # def validate_mobile(self, value):
    #     if not re.match(r'^01[3-9]\d{7}$', value):
    #         raise serializers.ValidationError('mobile incorrect')
    #     return value


    def create(self, validated_data):
        # user = super().create(validated_data)
        # user.set_password(validated_data['password'])
        # user.save()

        user = User.objects.create_user(**validated_data)
        return user