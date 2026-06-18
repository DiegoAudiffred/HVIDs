
import os

from django.apps import AppConfig
from transformers import pipeline


"""
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
"""
class IndexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'index'
    char_detector = None
    nsfw_detector = None

    def ready(self):
        import sys
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv or 'collectstatic' in sys.argv:
            return

        if os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv or not any(arg in sys.argv for arg in ['runserver', 'shell']):
            try:
                from transformers import pipeline
                print("\n" + "="*50)
                print("DEBUG: Iniciando carga de modelos...")
                
                self.char_detector = pipeline(
                    "image-classification", 
                    model="p1atdev/wd-eva02-large-tagger-v3", 
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

