
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import os
from django.conf import settings  # Importamos settings
from django.utils.translation import gettext_lazy as _

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
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)

    def __str__(self):
        return self.title

class Character(models.Model):
    name = models.CharField(max_length=255)    
    image = models.ImageField(upload_to="uploads/gallery/",blank=True, null=True)

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
    

class MediaFile(models.Model):
    #file = models.FileField(upload_to='media_files/%Y/%m/%d/')
    #thumbnail = models.ImageField(upload_to='media_files/thumbnails/%Y/%m/%d/', blank=True, null=True)
    title = models.CharField(max_length=255)
    artist= models.ForeignKey(Artist, on_delete=models.CASCADE,blank=True,null=True)
    tags = models.ManyToManyField(Tags, blank=True, null=True)
    game= models.ForeignKey(Game, on_delete=models.CASCADE,blank=True,null=True)
    hide = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    character= models.ForeignKey(Character, on_delete=models.CASCADE,blank=True,null=True)
    file = models.URLField(max_length=2000, blank=True, null=True)  # Almacenar la URL del archivo en Google Drive
    thumbnail = models.URLField(max_length=2000, blank=True, null=True)  # URL de la miniatura, si existe


    def __str__(self):
        return self.title
    
class comicImages(models.Model):
    mediaFile= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)
    pagNum = models.IntegerField()
    file = models.URLField(max_length=2000, blank=True, null=True)  # Almacenar la URL del archivo en Google Drive

class Comentario(models.Model):
    mediaFile= models.ForeignKey(MediaFile, on_delete=models.CASCADE,blank=True,null=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)

    comentario = models.CharField(max_length=400,blank=True, null=True)
