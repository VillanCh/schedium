#!/usr/bin/env python3
# coding:utf-8
import typing
import threading
from collections import OrderedDict
from datetime import datetime, timedelta


class SchediumTask(object):

    def __init__(self, target: typing.Callable, vargs: typing.Optional[tuple] = None,
                 kwargs: typing.Optional[dict] = None,
                 id: str = None, start: datetime = None, end: datetime = None,
                 interval: typing.Union[int, float] = None, first: bool = None,
                 next_time: datetime = None):
        self.target = target
        self.vargs = vargs
        self.kwargs = kwargs
        self.id = id
        self.start = start
        self.end = end
        self.interval = interval
        self.first = first

        self.next_time = next_time

    def is_finished(self):
        if self.end:
            return self.next_time > self.end
        else:
            return False

    def __repr__(self):
        return "<SchediumTask id:{}>".format(self.id)


class DefaultTaskHandler(object):

    def __init__(self):
        self.tasks = []
        self.tasks_table = {}

    def get_next_task(self):
        try:
            return self.tasks[0]
        except IndexError:
            return None

    def add_task(self, target: typing.Callable, vargs: typing.Optional[tuple] = None,
                 kwargs: typing.Optional[dict] = None,
                 id: str = None, start: datetime = None, end: datetime = None,
                 interval: typing.Union[int, float] = None, first: bool = None):
        if first:
            next_time = start or datetime.now()
        else:
            next_time = (start or datetime.now()) + timedelta(seconds=interval)

        task = SchediumTask(
            self.execute_target, (), {
                "target": target,
                "vargs": vargs,
                "kwargs": kwargs,
                "id": id,
            }, id, start, end, interval, first,
            next_time=next_time
        )
        self.tasks.append(task)
        self.tasks_table[task.id] = task

        self.update()

    def execute_target(self, target: typing.Callable, vargs: typing.Tuple, kwargs: typing.Mapping, id=None):
        # ret = threading.Thread(target=target, args=vargs, kwargs=kwargs)
        # ret.daemon = True
        # ret.start()
        target(*vargs, **kwargs)
        task: SchediumTask = self.tasks_table.get(id)
        if not task:
            return
        else:
            task.next_time += timedelta(seconds=task.interval)

            if task.is_finished():
                del self.tasks_table[task.id]
                if task in self.tasks:
                    self.tasks.remove(task)

            self.update()

    def update(self):
        self.tasks.sort(key=lambda x: x.next_time)

    def cancel(self, id):
        task = self.tasks_table.pop(id)
        if task in self.tasks:
            self.tasks.remove(task)
