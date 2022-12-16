from rest_framework import serializers
from .models import CustomUser
from django.utils.encoding import smart_str, smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .utils import Util


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'password2', 'user_type',)
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(validated_data['email'], validated_data['username'],
                                              validated_data['password'])
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)

    class Meta:
        model = CustomUser
        fields = ('email', 'password',)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'user_type',)


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, required=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"} ,required=True)

    class Meta:
        fields = ('password', 'password2',)

    def validate(self, data):
        user = self.context.get('user')
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(data['password'])
        user.save()
        return data


class SendResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=3)

    class Meta:
        fields = ('email')

    def validate(self, data):
        email = data.get('email', None)

        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uid = urlsafe_base64_encode(smart_bytes(user.id))
            print("uuid",uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("token", token)
            link = "http://localhost:3000/accounts/resetpassword/" + uid + "/" + token
            print("link",link)
            data = {'email_body': "Hi " + user.username + " Please use this link to reset your password " + link,
                    'email_subject': "Reset your password",
                    'to_email': user.email}
            Util.send_email(data)
            return data
        else:
            raise serializers.ValidationError({'email': 'Email does not exist.'})


class UserResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={"input_type": "password"}, required=True)
    password2 = serializers.CharField(max_length=255, style={"input_type": "password"} ,required=True)

    class Meta:
        fields = ('password', 'password2',)

    def validate(self, data):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            if data['password'] != data['password2']:
                raise serializers.ValidationError({'password': 'Passwords must match.'})
            id = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({'token': 'Token is not valid, please request a new one.'})
            user.set_password(data['password'])
            user.save()
            return data
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError({'token': 'Token is not valid, please request a new one.'})
