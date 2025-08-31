from django.urls import path, include
from prices import views as prices_views

urlpatterns = [
    path('api/', include('prices.api_urls')),
    path('', prices_views.index, name='index'),
]
