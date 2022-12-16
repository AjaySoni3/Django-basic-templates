from rest_framework.response import Response

from .models import CustomUser
from .renderers import UserRenderer
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, ChangePasswordSerializer, \
    SendResetPasswordSerializer, UserResetPasswordSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.contrib.auth import login, authenticate

from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterAPIView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({"msg": "Registrations Successful", "tokens": tokens}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


register_api_view = RegisterAPIView.as_view()


class LoginAPIView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                tokens = get_tokens_for_user(user)
                return Response({"msg": "Login Succesfull", "tokens": tokens}, status=status.HTTP_200_OK)
            return Response({"errors": "Please enter correct email address or password"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


login_api_view = LoginAPIView.as_view()


class UserProfile(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = self.request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


user_profile = UserProfile.as_view()


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


user_change_password = UserChangePasswordView.as_view()


class SendResetPasswordView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = SendResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Reset password link sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


send_reset_password = SendResetPasswordView.as_view()

class UserResetPasswordView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token):
        serializer = UserResetPasswordSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password Reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


user_reset_password = UserResetPasswordView.as_view()