from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI


# Singleton executor instance
executor = ProcessPoolExecutor()


def submit_task(fn: Callable, *args, **kwargs) -> Future:
    """Wrapper around the executor submit method"""
    return executor.submit(fn, *args, **kwargs)


@asynccontextmanager
async def executor_lifespan(app: FastAPI):
    yield
    executor.shutdown(wait=True)
