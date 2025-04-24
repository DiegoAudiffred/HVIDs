
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import os
from django.conf import settings  
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
    email = None  
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
    def tipo_objeto(self):
        return "juego"

class Character(models.Model):
    name = models.CharField(max_length=255)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return self.name
    def tipo_objeto(self):
        return "personaje"

    
class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Artist(models.Model):
    name = models.CharField(max_length=100)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
 
    def __str__(self):
        return self.name
    def tipo_objeto(self):
        return "artista"

class MediaFile(models.Model):
    name = models.CharField(max_length=255)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ManyToManyField(Character, blank=True)

    # Ahora se guarda el archivo localmente
    file = models.FileField(upload_to='media_files/%Y%m%d/', blank=True, null=True,max_length=255)
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    # Generación automática de thumbnail
    image = models.ImageField(upload_to='media_files/thumbnails/%Y%m%d/', blank=True, null=True)
    #isVideo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.file and not self.image:
            self.generate_thumbnail()
    @property
    def tipo_objeto(self):
        return "mediafile"

    def generate_thumbnail(self):
        try:
            clip = VideoFileClip(self.file.path)
            frame = clip.get_frame(10)  # segundo 1 del video
            image = Image.fromarray(frame)

            temp_thumb = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_thumb_path = temp_thumb.name
            temp_thumb.close()  

            image.save(temp_thumb_path, "JPEG")

            with open(temp_thumb_path, 'rb') as f:
                self.image.save(
                    f"{os.path.splitext(os.path.basename(self.file.name))[0]}_thumb.jpg",
                    ContentFile(f.read()),
                    save=False
                )

            os.unlink(temp_thumb_path)

            super().save()

        except Exception as e:
            print(f"Error al generar thumbnail: {e}")

class Comic(models.Model):
    name = models.CharField(max_length=100)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ManyToManyField(Character, blank=True)
    image = models.ImageField(upload_to='media_files/comicPortraits/', blank=True, null=True)
    #isVideo = models.BooleanField(default=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)

    @property
    def tipo_objeto(self):
        return "comic"

def comic_page_upload_to(instance, filename):
    comic_id = instance.comic.id if instance.comic.id else 'temp'
    filename = os.path.basename(filename)
    return f'comics/pages/{comic_id}/{filename}'

class ComicPage(models.Model):
    comic = models.ForeignKey(Comic, related_name='pages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=comic_page_upload_to)
    order = models.PositiveIntegerField(default=0)


class Comentario(models.Model):
    mediaFileID= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)
    comicID= models.ForeignKey(Comic, on_delete=models.CASCADE,blank=True,null=True)
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    comentario = models.CharField(max_length=400,blank=True, null=True)
