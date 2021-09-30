from rest_framework import serializers

from users.models import User

class AdminSerializers(serializers.ModelSerializer):

    class Meta:
        model=User
        fields='__all__'
        extra_kwargs={
            'password':{
                'write_only':True
            }
        }

    def create(self, validated_data):
        user = super(AdminSerializers, self).create(validated_data)
        user.is_staff = True
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        user = super(AdminSerializers, self).update(instance, validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user