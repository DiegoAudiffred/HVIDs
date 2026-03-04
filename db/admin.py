from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Tags)
admin.site.register(Artist)
admin.site.register(Character)
admin.site.register(Game)
admin.site.register(Comic)
admin.site.register(Comentario)
admin.site.register(ComicPage)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Notificacion)

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'user', 'uploaded_at', 'nsfw', 'hide')
    list_filter = ('uploaded_at', 'nsfw', 'hide', 'artist')
    search_fields = ('name', 'artist__name', 'user__username')
    readonly_fields = ('uploaded_at',)
    filter_horizontal = ('tags', 'character', 'likes')