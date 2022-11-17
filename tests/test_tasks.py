from unittest.mock import patch
from tasks import celery_tasks


def test_task():
    assert celery_tasks.create_task.run(1)
    assert celery_tasks.create_task.run(2)
    assert celery_tasks.create_task.run(3)

@patch("tasks.celery_tasks.create_task.run")
def test_mock_task(mock_run):
    assert celery_tasks.create_task.run(1)
    celery_tasks.create_task.run.assert_called_once_with(1)

    assert celery_tasks.create_task.run(2)
    assert celery_tasks.create_task.run.call_count == 2

    assert celery_tasks.create_task.run(3)
    assert celery_tasks.create_task.run.call_count == 3