from rest_framework import serializers
from django.contrib.auth.models import User # Usamos el modelo por defecto de Django

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True} # Para que la contraseña no se envíe de vuelta al Front
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user