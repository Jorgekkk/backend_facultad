from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrearPagoView, ProductoViewSet

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('crear-pago/', CrearPagoView.as_view()),
]