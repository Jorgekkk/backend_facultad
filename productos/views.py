import mercadopago
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer

# --- PARTE 1: ViewSet para listar productos (Mantenido por compatibilidad) ---
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


# --- PARTE 2: Vista para crear preferencia de pago con Mercado Pago ---
class CrearPagoView(APIView):
    def post(self, request):
        ACCESS_TOKEN = "APP_USR-3981250444573359-021718-b008900282be672295f585d88ec1da0e-3209594063"
        sdk = mercadopago.SDK(ACCESS_TOKEN)

        try:
            # 1. Verificamos si nos mandan un carrito completo o un solo producto
            carrito = request.data.get('carrito')
            items_mp = []

            if carrito and isinstance(carrito, list):
                print(f"🛒 Procesando pago de carrito con {len(carrito)} productos")
                # Armamos la lista para Mercado Pago
                for item in carrito:
                    items_mp.append({
                        "title": str(item.get('titulo', 'Producto VEN FCC')),
                        "quantity": 1,
                        "unit_price": float(item.get('precio', 0)),
                        "currency_id": "MXN"
                    })
            else:
                # Fallback por si compran directo un solo producto
                titulo = request.data.get('titulo')
                precio = request.data.get('precio')
                print(f"📦 Procesando pago individual para: {titulo} - ${precio}")
                
                if not titulo or precio is None:
                    return Response({'error': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)
                
                items_mp.append({
                    "title": str(titulo),
                    "quantity": 1,
                    "unit_price": float(precio),
                    "currency_id": "MXN"
                })

            # 2. Configuramos la preferencia con TODOS los items
            preference_data = {
                "items": items_mp,
                "back_urls": {
                    "success": "http://localhost:4200/exito",
                    "failure": "http://localhost:4200/error",
                    "pending": "http://localhost:4200/pendiente"
                }
            }

            preference_response = sdk.preference().create(preference_data)
            
            if preference_response["status"] in [200, 201]:
                return Response({'id': preference_response["response"]['id']}, status=status.HTTP_200_OK)
            else:
                print(f"❌ ERROR DETALLADO MP: {preference_response['response']}")
                return Response({'error': 'Error en Mercado Pago'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"❌ ERROR CRÍTICO: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)