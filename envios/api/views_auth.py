from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login con cookies HttpOnly",
        responses={200: OpenApiResponse(description="Login successful"), 401: OpenApiResponse(description="Invalid credentials")}
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"detail": "Successfully logged in."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout - elimina cookies de sesión",
        responses={200: OpenApiResponse(description="Logout successful")}
    )
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
