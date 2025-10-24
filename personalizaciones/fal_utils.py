"""
Utilidades para integrar Hugging Face en el proyecto
Funciones para generar imágenes reales usando Hugging Face Inference API
"""
import os
import json
import base64
from django.conf import settings
from PIL import Image
import io
import requests
import time

def get_hf_api_key():
    """Obtiene la API key de Hugging Face desde la configuración"""
    api_key = getattr(settings, 'HF_API_KEY', None)
    if not api_key:
        raise ValueError("HF_API_KEY no está configurada en settings.py")
    return api_key

def generate_design_from_prompt(user_prompt, item_type="camiseta"):
    """Genera un diseño personalizado basado en el prompt del usuario usando Hugging Face"""
    try:
        api_key = get_hf_api_key()
        
        # Usar Stable Diffusion XL para mejor calidad
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Preparar el prompt para diseño de estampado (NO incluir la prenda)
        enhanced_prompt = f"""
        {user_prompt}
        High quality, detailed design suitable for printing on clothing.
        Clean background, centered composition, vibrant colors, artistic style.
        Design element only, no clothing or fabric visible.
        """
        
        data = {
            "inputs": enhanced_prompt,
            "parameters": {
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
        }
        
        print(f"🎨 Generando imagen con Hugging Face para: '{user_prompt}'")
        
        # Hacer la solicitud a Hugging Face
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # La respuesta es directamente la imagen en bytes
            image_bytes = response.content
            
            # Convertir a base64 para el frontend
            image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                'concepto': f"Diseño generado: {user_prompt}",
                'elementos': "Imagen generada por Hugging Face Stable Diffusion",
                'colores': "Colores según el prompt",
                'estilo': "Realista y profesional",
                'ubicacion': "pecho",
                'tamaño': "mediano",
                'tipo_elemento': "imagen_real",
                'generated_by': 'huggingface',
                'user_prompt': user_prompt,
                'item_type': item_type,
                'image_data': image_data
            }
        elif response.status_code == 503:
            # Modelo cargándose, esperar un poco
            print("⏳ Modelo cargándose, esperando...")
            time.sleep(10)
            # Reintentar una vez
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                image_bytes = response.content
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                return {
                    'concepto': f"Diseño generado: {user_prompt}",
                    'elementos': "Imagen generada por Hugging Face Stable Diffusion",
                    'colores': "Colores según el prompt",
                    'estilo': "Realista y profesional",
                    'ubicacion': "pecho",
                    'tamaño': "mediano",
                    'tipo_elemento': "imagen_real",
                    'generated_by': 'huggingface',
                    'user_prompt': user_prompt,
                    'item_type': item_type,
                    'image_data': image_data
                }
        elif response.status_code == 429:
            print("⚠️ Límite de rate de Hugging Face alcanzado, usando generación local")
            return generate_local_design_from_prompt(user_prompt, item_type)
        else:
            print(f"Error de API Hugging Face: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"Error con Hugging Face API: {e}")
    
    # Fallback: usar generación local si Hugging Face falla
    return generate_local_design_from_prompt(user_prompt, item_type)

def generate_local_design_from_prompt(user_prompt, item_type="camiseta"):
    """Genera un diseño local como fallback"""
    prompt_lower = user_prompt.lower()
    
    # Analizar el prompt para determinar el tipo de diseño
    if any(word in prompt_lower for word in ['gato', 'perro', 'animal', 'mascota', 'cat', 'dog', 'pet']):
        tipo_elemento = 'animal'
        concepto = f"Animal: {user_prompt}"
        elementos = "Ilustración de animal con estilo cartoon"
        colores = "Colores vibrantes y llamativos"
        estilo = "Cartoon y divertido"
    elif any(word in prompt_lower for word in ['texto', 'frase', 'palabra', 'letra', 'text', 'word']):
        tipo_elemento = 'texto'
        concepto = f"Texto: {user_prompt}"
        elementos = "Tipografía moderna y elegante"
        colores = "Negro o colores contrastantes"
        estilo = "Minimalista y elegante"
    elif any(word in prompt_lower for word in ['geometrico', 'circulo', 'cuadrado', 'triangulo', 'geometric', 'circle', 'square']):
        tipo_elemento = 'geometrico'
        concepto = f"Geometría: {user_prompt}"
        elementos = "Formas geométricas modernas"
        colores = "Colores primarios y contrastantes"
        estilo = "Moderno y geométrico"
    elif any(word in prompt_lower for word in ['abstracto', 'arte', 'pintura', 'abstract', 'art', 'painting']):
        tipo_elemento = 'abstracto'
        concepto = f"Arte abstracto: {user_prompt}"
        elementos = "Formas abstractas y artísticas"
        colores = "Paleta de colores artística"
        estilo = "Artístico y abstracto"
    elif any(word in prompt_lower for word in ['logo', 'marca', 'empresa', 'brand', 'company']):
        tipo_elemento = 'logo'
        concepto = f"Logo: {user_prompt}"
        elementos = "Diseño de logo profesional"
        colores = "Colores corporativos"
        estilo = "Profesional y corporativo"
    else:
        tipo_elemento = 'mixto'
        concepto = f"Diseño personalizado: {user_prompt}"
        elementos = "Combinación de elementos visuales"
        colores = "Colores según el tema"
        estilo = "Personalizado y único"
    
    # Determinar ubicación basada en el tipo
    ubicacion = "pecho" if tipo_elemento in ['texto', 'logo'] else "pecho"
    tamaño = "mediano" if tipo_elemento in ['animal', 'abstracto'] else "pequeño"
    
    return {
        'concepto': concepto,
        'elementos': elementos,
        'colores': colores,
        'estilo': estilo,
        'ubicacion': ubicacion,
        'tamaño': tamaño,
        'tipo_elemento': tipo_elemento,
        'generated_by': 'local_fallback',
        'user_prompt': user_prompt,
        'item_type': item_type
    }

def create_image_from_design(design_data, width=400, height=400):
    """Crea una imagen basada en los datos del diseño"""
    try:
        # Si tenemos imagen de Hugging Face, convertirla
        if 'image_data' in design_data and design_data['image_data']:
            try:
                # Decodificar la imagen base64
                image_bytes = base64.b64decode(design_data['image_data'])
                img = Image.open(io.BytesIO(image_bytes))
                
                # Redimensionar si es necesario
                if img.size != (width, height):
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Convertir a PNG
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                return img_buffer
            except Exception as e:
                print(f"Error procesando imagen de Hugging Face: {e}")
        
        # Fallback: crear imagen local simple
        from PIL import ImageDraw, ImageFont
        
        img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        concepto = design_data.get('concepto', 'Diseño personalizado')
        tipo_elemento = design_data.get('tipo_elemento', 'texto')
        
        # Crear diseño simple basado en el tipo
        if tipo_elemento == 'texto':
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            text = concepto.split(':')[-1].strip()[:20]  # Primeros 20 caracteres
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(0, 0, 0), font=font)
            
        elif tipo_elemento == 'animal':
            # Dibujar un animal simple
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 6
            
            # Cuerpo
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        outline=(0, 0, 0), width=3)
            
            # Cabeza
            head_radius = radius // 2
            draw.ellipse([center_x - head_radius, center_y - head_radius - radius//2, 
                         center_x + head_radius, center_y - head_radius + radius//2], 
                        outline=(0, 0, 0), width=2)
            
            # Ojos
            eye_size = 2
            draw.ellipse([center_x - head_radius//2 - eye_size, center_y - head_radius//2 - eye_size,
                         center_x - head_radius//2 + eye_size, center_y - head_radius//2 + eye_size],
                        fill=(0, 0, 0))
            draw.ellipse([center_x + head_radius//2 - eye_size, center_y - head_radius//2 - eye_size,
                         center_x + head_radius//2 + eye_size, center_y - head_radius//2 + eye_size],
                        fill=(0, 0, 0))
        
        else:
            # Diseño por defecto
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 4
            
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        outline=(0, 0, 0), width=4)
        
        # Guardar imagen
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
        
    except Exception as e:
        print(f"Error creando imagen: {e}")
        # Imagen de error
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, height//2), "Error generando diseño", fill=(255, 0, 0))
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer

def test_hf_connection():
    """Prueba la conexión con Hugging Face"""
    try:
        api_key = get_hf_api_key()
        if not api_key:
            return False, "API key no configurada"
        
        # Probar con una solicitud simple
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "inputs": "A simple test image",
            "parameters": {
                "num_inference_steps": 10,
                "width": 256,
                "height": 256
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return True, f"Conexión exitosa con Hugging Face. Imagen generada: {len(response.content)} bytes"
        elif response.status_code == 503:
            return True, "Conexión exitosa con Hugging Face (modelo cargándose)"
        elif response.status_code == 429:
            return False, "Límite de rate alcanzado en Hugging Face"
        else:
            return False, f"Error de API: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"