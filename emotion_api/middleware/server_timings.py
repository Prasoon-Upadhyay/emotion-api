import contextlib
from contextlib import contextmanager
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from ..literals import ServiceDescriptors
from rest_framework.response import Response
import threading
import time

_thread_local = threading.local()

class TimedService:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._start = None
        self._end = None

    def start(self):
        self._start = time.time_ns()
        add_service(self)

    def end(self):
        self._end = time.time_ns()

    @property
    def duration(self):
        if self._start is not None:
            with contextlib.suppress(ZeroDivisionError):
                return int(((self._end or time.time_ns()) - self._start) / 1_000_000)
        return 0

    def __str__(self):
        return f'{self.name};desc="{self.description}";dur={self.duration}'


def add_service(service: "TimedService"):
    services = get_services()
    services.append(service)


def get_services() -> list["TimedService"]:
    return _thread_local.__dict__.setdefault("services", [])


def discard_all_services():
    _thread_local.__dict__["services"] = []


@contextmanager
def timed(name: str, description: str = ""):
    """
    Context manager for measuring execution time of a block
    and exposing it through Server-Timing headers.
    """
    service = TimedService(name, description)
    service.start()
    try:
        yield service
    finally:
        service.end()


def timed_wrapper(name: str, description: str = ""):
    """
    Decorator version of the timed context manager.
    """

    def wrapper(function):
        def func(*args, **kwargs):
            service = TimedService(name, description)
            service.start()

            result = function(*args, **kwargs)

            service.end()
            return result

        return func

    return wrapper


class ServerTiming(MiddlewareMixin):

    def process_response(self, request, response: Response):

        services_dict = {}
        total_time = 0

        # Aggregated timing buckets (project-specific)
        service_timing_mapper = {
            ServiceDescriptors.API: 0,
            ServiceDescriptors.PREPROCESS: 0,
            ServiceDescriptors.FEATURE: 0,
            ServiceDescriptors.PREDICTION: 0,
            ServiceDescriptors.COMPUTE: 0,
            ServiceDescriptors.DB: 0,
            ServiceDescriptors.CACHE: 0,
            ServiceDescriptors.EXTERNAL_API: 0,
        }

        for service in get_services():

            duration = service.duration

            if duration != 0:

                if service.name in service_timing_mapper:
                    service_timing_mapper[service.name] += duration

            key = f'{service.name};desc="{service.description}'
            total_time += duration

            if key not in services_dict:
                services_dict[key] = duration
            else:
                services_dict[key] += duration


        services = [service + f'";dur={dur}' for service, dur in services_dict.items()]

        if services:
            services.append(f'total;desc="Total";dur={total_time}')

            response.headers["Server-Timing"] = ",".join(services)

        discard_all_services()

        return response