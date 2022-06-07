from celery import Celery


app = Celery('task', broker='amqp://localhost')


@app.task
def task_manager(data):
    return data