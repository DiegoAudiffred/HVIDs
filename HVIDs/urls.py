
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from index import views as index
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('index.urls')),
    #path('login/', include('index.urls')),
    path('login/', include(('login.urls', 'login'), namespace='login')),
    path('', include(('index.urls', 'index'), namespace='index')),  # app principal en raíz
    
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = index.error_404
handler500 = index.error_500
