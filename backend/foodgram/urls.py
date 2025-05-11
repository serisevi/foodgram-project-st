from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from api.views import ShortLinkRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>/', ShortLinkRedirectView.as_view(), name='short-link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
