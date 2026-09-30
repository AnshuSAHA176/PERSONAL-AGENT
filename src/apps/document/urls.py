from rest_framework.routers import DefaultRouter
from .views import DocumentView
from django.urls import path,include

router = DefaultRouter()
router.register("",DocumentView,basename='document')


urlpatterns=[
    path('',include(router.urls),name='document')
]