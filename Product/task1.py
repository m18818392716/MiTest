
from celery import Celery
from MiDuoTester.celery import app
from celery import task
from celery import shared_task

@app.task
def add(x, y):
    print("计算2个值的和: %s %s" % (x, y))
    return x+y


@task()
# @shared_task
def add(x, y):
    print("%d + %d = %d" % (x, y, x + y))
    return x + y


# class AddClass(Task):
#    def run(x,y):
#        print "%d + %d = %d"%(x,y,x+y)
#        return x+y
# tasks.register(AddClass)

@shared_task
def mul(x, y):
    print
    "%d * %d = %d" % (x, y, x * y)
    return x * y


@shared_task
def sub(x, y):
    print("%d - %d = %d" % (x, y, x - y))
    return x - y