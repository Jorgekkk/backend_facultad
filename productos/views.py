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
        # Access Token de prueba
        ACCESS_TOKEN = "APP_USR-3981250444573359-021718-b008900282be672295f585d88ec1da0e-3209594063"
        sdk = mercadopago.SDK(ACCESS_TOKEN)

        try:
            # 1. Extraemos los datos que vienen de Supabase/Angular
            titulo = request.data.get('titulo')
            precio = request.data.get('precio')
            
            # Limpieza de datos básica para evitar errores de tipo
            if titulo:
                titulo = str(titulo).strip()
            
            print(f"📦 Procesando pago para: {titulo} - ${precio}")

            if not titulo or precio is None:
                return Response({'error': 'Faltan datos críticos: titulo o precio'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Convertimos el precio a float para Mercado Pago
            try:
                precio_final = float(precio)
            except (ValueError, TypeError):
                return Response({'error': 'El formato del precio es inválido'}, status=status.HTTP_400_BAD_REQUEST)

            # 3. Configuramos la preferencia con los datos REALES
            preference_data = {
                "items": [
                    {
                        "title": titulo,
                        "quantity": 1,
                        "unit_price": precio_final,
                        "currency_id": "MXN"
                    }
                ],
                "back_urls": {
                    "success": "http://localhost:4200/exito",
                    "failure": "http://localhost:4200/error",
                    "pending": "http://localhost:4200/pendiente"
                },
                #"auto_return": "approved",
            }

            # 4. Intentamos crear la preferencia en Mercado Pago
            preference_response = sdk.preference().create(preference_data)
            
            # 5. Analizamos la respuesta del SDK
            if preference_response["status"] in [200, 201]:
                pref_id = preference_response["response"]['id']
                print(f"✅ Preferencia creada con éxito: {pref_id}")
                return Response({'id': pref_id}, status=status.HTTP_200_OK)
            else:
                # ESTO ES VITAL: Si hay error, imprimimos el detalle real de Mercado Pago
                print(f"❌ ERROR DETALLADO DE MERCADO PAGO: {preference_response['response']}")
                return Response({
                    'error': 'Mercado Pago rechazó la preferencia',
                    'detalle': preference_response['response']
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN EL BACKEND: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)