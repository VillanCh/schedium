#!/usr/bin/env python3
# coding:utf-8
import uuid
import typing
from datetime import datetime, timedelta
from threading import Timer, Thread
import time

from .handlers import DefaultTaskHandler


class _CurrentTask(Timer):

    def __init__(self, id: str, next_execute_time: datetime, target: typing.Callable, vargs: tuple = (),
                 kwargs: typing.Optional[typing.Mapping[str, typing.Any]] = None):
        self.next_execute_time: datetime = next_execute_time
        interval = max(next_execute_time.timestamp() - time.time(), 0)
        self.id = id

        Timer.__init__(self, interval=interval, function=target, args=vargs, kwargs=kwargs)
        Timer.daemon = True


class Schedium(object):

    def __init__(self, task_handler=None):
        self._task_handler = task_handler or DefaultTaskHandler()
        self._current_task: typing.Optional[_CurrentTask] = None

        self.update()

    def execute_later(self, after: typing.Union[int, float], target: typing.Callable, vargs: tuple = (),
                      kwargs: typing.Optional[typing.Mapping[str, str]] = None, id: str = None):
        _id = id or uuid.uuid4().hex
        now = datetime.now()
        interval = timedelta(seconds=after)
        end = now + interval
        self._task_handler.add_task(target=target, vargs=vargs, kwargs=kwargs, id=_id, start=now, end=end,
                                    interval=interval.total_seconds(), first=False)
        self.update()

    def execute_now(self, target: typing.Callable, vargs: typing.Optional[tuple] = None,
                    kwargs: dict = None):
        self._task_handler.execute_target(target, vargs or (), kwargs or {})

    def execute_interval(self, interval: typing.Union[int, float], target: typing.Callable,
                         vargs: typing.Optional[tuple] = None,
                         kwargs: typing.Optional[typing.Mapping[str, str]] = None,
                         first: bool=True, start: typing.Optional[datetime]=None,
                         end: typing.Optional[datetime]=None, id=None):
        id = id or uuid.uuid4().hex

        if all([start, end]):
            if start > end:
                return

        self._task_handler.add_task(
            target=target,
            vargs=vargs or (),
            kwargs=kwargs or {},
            id=id,
            start=start,
            end=end,
            interval=interval,
            first=first
        )
        self.update()

    def update(self):
        task = self._task_handler.get_next_task()

        if not task:
            return

        if self._current_task:
            # still current task
            if task.id == self._current_task.id and task.next_time == self._current_task.next_execute_time:
                return

            if self._current_task.is_alive():
                self._current_task.cancel()

        self._current_task = _CurrentTask(
            id=task.id, next_execute_time=task.next_time, target=self._execute,
            vargs=(), kwargs={
                "target": task.target,
                "vargs": task.vargs,
                "kwargs": task.kwargs,
            }
        )
        self._current_task.daemon = True
        self._current_task.start()

    def cancel(self, id):
        if self._current_task.id == id:
            self._current_task.cancel()
            self._current_task = None
        return self._task_handler.cancel(id)

    def _execute(self, target, vargs, kwargs):
        target(*vargs, **kwargs)
        self.update()