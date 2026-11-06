from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap

from core.views import home
from .sitemaps import CodeShotSitemap

sitemaps = {
    'default': CodeShotSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path(
        'sitemap.xml', 
        sitemap, 
        {'sitemaps': sitemaps}, 
        name='django.contrib.sitemaps.views.sitemap'),
]