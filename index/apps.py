import os

from django.apps import AppConfig
from transformers import pipeline

import os
from django.apps import AppConfig
import os
from django.apps import AppConfig

class IndexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'index'
    char_detector = None
    nsfw_detector = None

    def ready(self):
        import sys
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            try:
                from transformers import pipeline
                print("\n" + "="*50)
                print("DEBUG: Iniciando carga de modelos...")
                
                # Agregamos trust_remote_code=True para desbloquear el modelo
                self.char_detector = pipeline(
                    "image-classification", 
                    model="p1atdev/wd-swinv2-tagger-v3-hf", 
                    trust_remote_code=True,
                    device=-1
                )
                print("DEBUG: Modelo de Personajes/Tags cargado correctamente.")
                
                self.nsfw_detector = pipeline(
                    "image-classification", 
                    model="AdamCodd/vit-base-nsfw-detector", 
                    device=-1
                )
                print("DEBUG: Modelo NSFW cargado correctamente.")
                print("="*50 + "\n")
                
            except Exception as e:
                print(f"\nDEBUG ERROR CRÍTICO AL INICIAR IA: {e}\n")