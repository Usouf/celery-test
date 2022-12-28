from django.urls import path, include

from rest_framework import routers

from . import views


app_name = 'tasks'

router = routers.SimpleRouter()
router.register('some', views.SomeModelViewSet, basename='some')
router.register('count', views.CountViewSet, basename='count')

urlpatterns = [
    path('', views.GenericCall.as_view()),
    path('results/<task_id>/', views.CallStatus.as_view(), name='result'),
    path('schedule/', views.ScheduleTask.as_view(), name='schedule'),
    path('api/', include(router.urls)),
]
