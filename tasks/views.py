import datetime
import logging

from rest_framework import generics, response, status, viewsets, serializers
from rest_framework.decorators import action

from celery.result import AsyncResult

from .celery_tasks import create_task, count_model_items, scheduled_task
from .models import SomeModel, NumberOfSomeModelItems

log = logging.getLogger("tasks")

class GenericCall(generics.GenericAPIView):

    def get(self, request):
        task_type = request.data.get('type')
        task = create_task.delay(int(task_type))
        return response.Response({'task': task.id}, status=status.HTTP_200_OK)

class CallStatus(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('task_id')
        task_result = AsyncResult(task_id)
        return response.Response({
            'task_id': task_id,
            'task_status': task_result.status,
            'task_result': task_result.result
        }, status=status.HTTP_200_OK)


class SomeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SomeModel
        exclude = ()

class SomeModelViewSet(viewsets.ModelViewSet):
    serializer_class = SomeModelSerializer
    queryset = SomeModel.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @action(methods=['post'], detail=False, url_path="count")
    def count(self, request, *args, **kwargs):
        count_model_items.delay()
        return response.Response(status=status.HTTP_200_OK)

class CountSerializer(serializers.ModelSerializer):

    class Meta:
        model = NumberOfSomeModelItems
        exclude = ()

class CountViewSet(viewsets.ModelViewSet):
    serializer_class = CountSerializer
    queryset = NumberOfSomeModelItems.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class ScheduleTask(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        task = scheduled_task.apply_async(eta=datetime.datetime(2022, 11, 16, 13, 20))
        log.info('task id: %s', task.id)
        return response.Response(status=status.HTTP_200_OK)

