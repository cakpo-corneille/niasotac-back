from django.urls import path, include
from .api.v1 import router

app_name = 'showcase'

urlpatterns = [
    path('', include(router.urls)),
]
