# Proyecto CECILIA

## Descripción
CECILIA es una plataforma web para la personalización y compra de prendas de vestir, desarrollada con Django. Permite a los usuarios diseñar camisetas y hoodies, agregar productos personalizados al carrito y realizar compras.

## Requisitos
- Python 3.13+
- Django 4.2+
- Base de datos SQLite (por defecto)

## Ejecución
1. Clona el repositorio y accede a la carpeta principal:
	```bash
	cd ProjectCECILIA
	```
 2. Instalar dependencias con:
	```bash
	pip install -r requirements.txt
	```
3. Realiza las migraciones:
	```bash
	python manage.py migrate
	```
4. (Opcional) Crea un superusuario para acceder al admin:
	```bash
	python manage.py createsuperuser
	```
5. Ejecuta el servidor de desarrollo:
	```bash
	python manage.py runserver
	```

## Ruta principal
- Accede a la aplicación en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- La página principal muestra el catálogo de productos.
- Para personalizar y comprar, debes iniciar sesión.

## Funcionalidades principales
- Catálogo de productos: `/` (home)
- Detalle de producto: `/items/<id>/`
- Personalización: `/personalizaciones/personalizar/<id>/`
- Carrito de compras: `/cart/`
- Compra de productos: botón "Buy" en el carrito


## Notas
- Los productos personalizados se agregan y gestionan desde el carrito principal.
- El panel de administración está disponible en `/admin/`.

## Contacto
Para dudas o soporte, contacta al equipo de desarrollo.

## Integrantes
- Juan Simón Ospina
- Sebastián Durán
- Thomas Buitrago
