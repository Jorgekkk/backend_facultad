import mercadopago
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Producto
from .serializers import ProductoSerializer

# --- PARTE 1: ViewSet para listar productos ---
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


# --- PARTE 2: Vista para crear preferencia de pago con Mercado Pago ---
class CrearPagoView(APIView):
    def post(self, request):
        # ✅ Tu Access Token de prueba (correcto)
        ACCESS_TOKEN = "APP_USR-3981250444573359-021718-b008900282be672295f585d88ec1da0e-3209594063"
        
        sdk = mercadopago.SDK(ACCESS_TOKEN)

        try:
            # Obtener el ID del producto desde la petición
            producto_id = request.data.get('id')
            
            # 🔍 DEBUGGING: Ver qué datos llegan
            print(f"📦 Datos recibidos: {request.data}")
            print(f"🆔 ID del producto: {producto_id}")
            
            # Validar que llegó el ID
            if not producto_id:
                print("❌ ERROR: No se proporcionó el ID del producto")
                return Response(
                    {'error': 'No se proporcionó el ID del producto'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar el producto en la base de datos
            try:
                producto = Producto.objects.get(id=producto_id)
                print(f"✅ Producto encontrado: {producto.nombre} - ${producto.precio}")
            except Producto.DoesNotExist:
                print(f"❌ ERROR: Producto con ID {producto_id} no existe")
                return Response(
                    {'error': f'Producto con ID {producto_id} no existe'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Crear la preferencia de pago
            preference_data = {
                "items": [
                    {
                        "title": producto.nombre,
                        "quantity": 1,
                        "unit_price": float(producto.precio),
                        "currency_id": "MXN"
                    }
                ],
                "back_urls": {
                    "success": "http://localhost:4200/exito",
                    "failure": "http://localhost:4200/error",
                    "pending": "http://localhost:4200/pendiente"
                },
            }
            
            print(f"📤 Enviando a Mercado Pago: {preference_data}")

            # Crear la preferencia en Mercado Pago
            preference_response = sdk.preference().create(preference_data)
            
            print(f"📥 Respuesta de Mercado Pago: {preference_response}")
            
            # Verificar la respuesta
            if preference_response["status"] == 200 or preference_response["status"] == 201:
                preference = preference_response["response"]
                print(f"✅ Preferencia creada exitosamente: {preference['id']}")
                return Response({'id': preference['id']}, status=status.HTTP_200_OK)
            else:
                print(f"❌ ERROR de Mercado Pago: {preference_response}")
                return Response(
                    {
                        'error': 'Error al crear preferencia en Mercado Pago',
                        'detalle': preference_response
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            # Capturar cualquier otro error
            print(f"❌ ERROR INTERNO: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )