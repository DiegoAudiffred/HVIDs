
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
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.contrib.auth.models import User
class UserManager(BaseUserManager):
    """Define a model manager for User model with a username field instead of an email."""

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model using username and password only."""

    username = models.CharField("Usuario", max_length=15, unique=True, null=False, blank=False)
    image = models.ImageField(upload_to="uploads/gallery/", blank=True, null=True)
    banner = models.ImageField(upload_to="uploads/gallery/", blank=True, null=True)
    can_upload = models.BooleanField(default=True)
#    can_edit = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    can_nsfw = models.BooleanField(default=True)
    # Campo para seguir usuarios
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,null=True
    )

    email = None
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return str(self.username)

    def follow(self, user):
        """Seguir a otro usuario."""
        self.following.add(user)

    def unfollow(self, user):
        """Dejar de seguir a otro usuario."""
        self.following.remove(user)

    def is_following(self, user):
        """Verifica si sigue a un usuario."""
        return self.following.filter(id=user.id).exists()

    def is_followed_by(self, user):
        """Verifica si es seguido por un usuario."""
        return self.followers.filter(id=user.id).exists()

class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Game(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_game', blank=True)

    def total_likes(self):
        return self.likes.count()
 
    def __str__(self):
        return self.name
    def tipo_objeto(self):
        return "game"

    
class Character(models.Model):
    GENDER_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('femboy', 'Femboy'),

    ]
    name = models.CharField(max_length=255)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE,blank=True,null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='female')    
    tags = models.ManyToManyField(Tags, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)#,max_length=255
    social_media = models.JSONField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_character', blank=True)
    
    def total_likes(self):
        return self.likes.count()
    def __str__(self):
        return self.name
    def tipo_objeto(self):
        return "character"

    
    
class Artist(models.Model):
    GENDER_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('femboy', 'Femboy'),

    ]
    name = models.CharField(max_length=100,unique=True)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='female')    
    tags = models.ManyToManyField(Tags, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    social_media = models.JSONField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_artist', blank=True)

    def total_likes(self):
        return self.likes.count()
    def __str__(self):
        return self.name
    def tipo_objeto(self):
        return "artist"

class MediaFile(models.Model):
    name = models.CharField(max_length=255)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ManyToManyField(Character, blank=True)
    nsfw = models.BooleanField(default=False)
    file = models.FileField(upload_to='media_files/%Y%m%d/', blank=True, null=True,max_length=255)
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    image = models.ImageField(upload_to='media_files/thumbnails/%Y%m%d/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_mediafiles', blank=True)
    original_link = models.URLField(blank=True, null=True)

    def total_likes(self):
        return self.likes.count()
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
    user=models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_comic', blank=True)
    nsfw = models.BooleanField(default=False)
    original_link = models.URLField(blank=True, null=True)
    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.name
    @property
    def tipo_objeto(self):
        return "comic"


class Post(models.Model):
    name = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(max_length=500)
    #tags = models.ManyToManyField('Tags', blank=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_post', blank=True)

    def __str__(self):
        return self.name

    def total_likes(self):
        return self.likes.count()

    @property
    def tipo_objeto(self):
        return "post"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media_files/postImages/')

    
def comic_page_upload_to(instance, filename):
    comic_id = instance.comic.id if instance.comic.id else 'temp'
    filename = os.path.basename(filename)
    return f'comics/pages/{comic_id}/{filename}'

class ComicPage(models.Model):
    comic = models.ForeignKey(Comic, related_name='pages', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=comic_page_upload_to)
    order = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tags, blank=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.comic.name

class Comentario(models.Model):
    mediaFileID= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)
    comicID= models.ForeignKey(Comic, on_delete=models.CASCADE,blank=True,null=True)    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    comentario = models.CharField(max_length=400,blank=True, null=True)
    
class Notificacion(models.Model):
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    emisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    # Campos para GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    contenido_objeto = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Notificación para {self.destinatario}"
