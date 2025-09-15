from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, tipo_usuario, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre=nombre, tipo_usuario=tipo_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre, tipo_usuario='administrador', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo, nombre, tipo_usuario, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('empresa', 'Empresa'),
        ('administrador', 'Administrador'),
    ]
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'tipo_usuario']


    class Meta:
        abstract = False

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_usuario_display()})"


# Modelo para empresa con dirección
class Empresa(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='empresa')
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return f"Empresa: {self.usuario.nombre} - Dirección: {self.direccion}"
