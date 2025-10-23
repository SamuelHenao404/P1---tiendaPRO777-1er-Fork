"""
Utilidades para integrar Gemini AI en el proyecto - DESHABILITADO
Todas las funciones de IA han sido comentadas para eliminar la funcionalidad de generación de imágenes con IA
"""
import os
import requests
import json
from django.conf import settings

# FUNCIONES DE IA DESHABILITADAS - Todas las funciones relacionadas con Gemini AI han sido comentadas
# para eliminar la funcionalidad de generación de imágenes con IA

def get_gemini_api_key():
    """Obtiene la API key de Gemini desde la configuración - DESHABILITADA"""
    raise ValueError("La funcionalidad de IA ha sido deshabilitada")

# def generate_design_description(item_title, item_category):
#     """Genera una descripción de diseño personalizada usando Gemini AI - DESHABILITADA"""
#     return f"Diseño personalizado para {item_title} - {item_category}"

# def suggest_design_ideas(user_preferences):
#     """Sugiere ideas de diseño basadas en las preferencias del usuario - DESHABILITADA"""
#     return [
#         "Diseño minimalista con tipografía elegante",
#         "Patrón geométrico moderno y colorido",
#         "Ilustración artística con estilo vintage",
#         "Logo corporativo profesional y limpio",
#         "Diseño abstracto con colores vibrantes"
#     ]

# def generate_design_from_prompt(user_prompt, item_type="camiseta"):
#     """Genera un diseño personalizado basado en el prompt del usuario usando Gemini AI - DESHABILITADA"""
#     return {
#         'concepto': f"Diseño personalizado basado en: {user_prompt}",
#         'elementos': "Texto personalizado y elementos gráficos",
#         'colores': "Colores según preferencia del usuario",
#         'estilo': "Moderno y personalizado",
#         'ubicacion': "pecho",
#         'tamaño': "mediano",
#         'tipo_elemento': "texto",
#         'generated_by': 'ai',
#         'user_prompt': user_prompt,
#         'item_type': item_type
#     }

# Todas las demás funciones de IA han sido comentadas para deshabilitar la funcionalidad
# Las funciones incluyen:
# - parse_design_response
# - generate_svg_design
# - extract_main_color
# - extract_secondary_color
# - generate_animal_svg
# - generate_logo_svg
# - generate_pattern_svg
# - generate_symbol_svg
# - generate_text_svg
# - detect_animal_type
# - extract_text_from_prompt
# - create_image_from_design
# - create_animal_image
# - create_logo_image
# - create_pattern_image
# - create_symbol_image
# - create_text_image
# - create_space_image
# - create_nature_image
# - create_fantasy_image
# - test_gemini_connection

# NOTA: Este archivo contenía más de 1200 líneas de código para la generación de imágenes con IA.
# Todas las funciones han sido comentadas para eliminar completamente la funcionalidad de IA.
# Si necesitas restaurar alguna funcionalidad específica, puedes descomentar las funciones correspondientes.