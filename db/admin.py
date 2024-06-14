
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Tags)
admin.site.register(MediaFile)
admin.site.register(Artist)
admin.site.register(Character)
admin.site.register(Game)

