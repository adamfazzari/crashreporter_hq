from celery import Celery

celery = Celery('crashreporter_hq', broker='redis://localhost:6379/0')


@celery.task(name='tasks.send_status_report')
def send_status_report(arg1, arg2):
    # some long running task here
    print arg1, arg2
    with open('/tmp/testing_redis.temp', 'w') as f:
        pass
    return arg1, arg2
