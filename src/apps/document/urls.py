from rest_framework.routers import DefaultRouter
from .views import DocumentView,SimilarityView
from django.urls import path,include

router = DefaultRouter()
router.register("",DocumentView,basename='document')


urlpatterns=[
    path('similar/',SimilarityView.as_view(),name='similar chunks'),
    path('',include(router.urls),name='document')
]