"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from config.api_routers import router_v1, router_v2
from envios.api.views_auth import LoginView, LogoutView

urlpatterns = [
    path('admin/',   admin.site.urls),
    
    # ── Swagger Docs ──────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ── API REST v1 ───────────────────────────────────────
    path('api/v1/', include(router_v1.urls)),
    path('api/v1/auth/token/',        TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/',TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/v1/auth/login/',        LoginView.as_view(),            name='api_login'),
    path('api/v1/auth/logout/',       LogoutView.as_view(),           name='api_logout'),

    # ── API REST v2 ───────────────────────────────────────
    path('api/v2/', include(router_v2.urls)),

    # ── Vistas web ───────────────────────────────────────
    path('',         include('envios.urls', namespace='envios')),
    path('login/',   auth_views.LoginView.as_view(template_name='accounts/login.html'),  name='login'),
    path('logout/',  auth_views.LogoutView.as_view(),                                    name='logout'),
]
