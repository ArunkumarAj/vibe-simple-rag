"""
URL configuration for rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Import API views
from api.upload_pdf import PDFUploadView
from api.chat import ChatView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/upload_pdf/', PDFUploadView.as_view(), name='upload_pdf'),
    path('api/chat/', ChatView.as_view(), name='chat_with_pdf'),
    
    # Frontend - Serve index.html for the root path and any other unhandled paths (for SPA-like behavior)
    # This ensures that refreshing a frontend route still serves the index.html
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    # path('<path:resource>', TemplateView.as_view(template_name='index.html')), # Catch-all for SPA if needed
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

print("Django URL patterns loaded.")
print(f"Static files will be served from: {settings.STATICFILES_DIRS}")