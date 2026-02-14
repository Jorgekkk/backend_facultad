from django.db import models

class Producto(models.Model):
    CATEGORIAS = [
        ('COMIDA', 'Comida'),
        ('DIVERSION', 'Objetos de Diversión'),
        ('USO', 'Objetos de Uso'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    vendedor_nombre = models.CharField(max_length=100)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    imagen_url = models.URLField(blank=True, null=True) # Aquí pegaremos el link de Supabase Storage

    def __str__(self):
        return self.nombre