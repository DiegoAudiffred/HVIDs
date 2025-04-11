
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import os
from django.conf import settings  # Importamos settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.files.base import ContentFile
from moviepy import VideoFileClip
from PIL import Image
import os
import tempfile

class UserManager(BaseUserManager):
    """Define a model manager for User model with a username field instead of an email."""

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """Create and save a User with the given username and password."""
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        """Create and save a regular User with the given username and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """Create and save a SuperUser with the given username and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

class User(AbstractUser):
    """Custom user model using username and password only."""

    username = models.CharField("Usuario", max_length=15, unique=True, null=False, blank=False)
    email = None  # Remove the email field if it's not necessary
    REQUIRED_FIELDS = []
    objects = UserManager()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.username)
    
class Game(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)

    def __str__(self):
        return self.name

class Character(models.Model):
    name = models.CharField(max_length=255)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return self.name

    
class Tags(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Artist(models.Model):
    name = models.CharField(max_length=100)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
 
    def __str__(self):
        return self.name
    

#class MediaFile(models.Model):
#    #file = models.FileField(upload_to='media_files/%Y/%m/%d/')
#    #thumbnail = models.ImageField(upload_to='media_files/thumbnails/%Y/%m/%d/', blank=True, null=True)
#    name = models.CharField(max_length=255)
#    artist= models.ForeignKey(Artist, on_delete=models.CASCADE,blank=True,null=True)
#    tags = models.ManyToManyField(Tags, blank=True, null=True)
#    game= models.ForeignKey(Game, on_delete=models.CASCADE,blank=True,null=True)
#    hide = models.BooleanField(default=False)
#    uploaded_at = models.DateTimeField(auto_now_add=True)
#    character= models.ManyToManyField(Character, blank=True, null=True)
#    file = models.URLField(max_length=2000, blank=True, null=True)  # Almacenar la URL del archivo en Google Drive
#    thumbnail = models.URLField(max_length=2000, blank=True, null=True)  # URL de la miniatura, si existe
#    #thumbnail = models.ImageField(upload_to="uploads/thumbnails/",blank=True, null=True)
#    isVideo = models.BooleanField(default=True)
#    
#    
#    def __str__(self):
#        return self.name


class MediaFile(models.Model):
    name = models.CharField(max_length=255)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ManyToManyField(Character, blank=True)

    # Ahora se guarda el archivo localmente
    file = models.FileField(upload_to='media_files/%Y/%m/%d/', blank=True, null=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    # Generación automática de thumbnail
    thumbnail = models.ImageField(upload_to='media_files/thumbnails/%Y/%m/%d/', blank=True, null=True)
    isVideo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.isVideo and self.file and not self.thumbnail:
            self.generate_thumbnail()

    def generate_thumbnail(self):
        try:
            clip = VideoFileClip(self.file.path)
            frame = clip.get_frame(10)  # segundo 1 del video
            image = Image.fromarray(frame)

            # Crear archivo temporal para guardar el frame como imagen
            temp_thumb = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_thumb_path = temp_thumb.name
            temp_thumb.close()  # Muy importante: cerramos para evitar conflicto en Windows

            # Guardar el frame como imagen JPEG
            image.save(temp_thumb_path, "JPEG")

            # Leer el archivo y guardar en el ImageField
            with open(temp_thumb_path, 'rb') as f:
                self.thumbnail.save(
                    f"{os.path.splitext(os.path.basename(self.file.name))[0]}_thumb.jpg",
                    ContentFile(f.read()),
                    save=False
                )

            # Eliminar archivo temporal una vez terminado
            os.unlink(temp_thumb_path)

            # Guardar la instancia con el thumbnail actualizado
            super().save()

        except Exception as e:
            print(f"Error al generar thumbnail: {e}")



#class comicImages(models.Model):
#    mediaFile= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)
#    pagNum = models.IntegerField()
#    file = models.URLField(max_length=2000, blank=True, null=True)  # Almacenar la URL del archivo en Google Drive

class Comic(models.Model):
    name = models.CharField(max_length=100)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ManyToManyField(Character, blank=True)

def comic_page_upload_to(instance, filename):
    # Si el cómic aún no ha sido guardado y no tiene ID, usa un placeholder temporal
    comic_id = instance.comic.id if instance.comic.id else 'temp'
    filename = os.path.basename(filename)
    return f'comics/pages/{comic_id}/{filename}'

class ComicPage(models.Model):
    comic = models.ForeignKey(Comic, related_name='pages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=comic_page_upload_to)
    order = models.PositiveIntegerField(default=0)


class Comentario(models.Model):
    mediaFile= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    comentario = models.CharField(max_length=400,blank=True, null=True)
