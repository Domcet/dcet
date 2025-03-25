import functools
import asyncio
from dcet_tools.dcet_logging import BaseLogging


def catch_exception(logger_name: str):
    logger = BaseLogging(logger_name)

    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as ex:
                    logger.error(
                        exception=ex,
                        message=str(ex)
                    )
                    raise ex
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    logger.error(
                        exception=ex,
                        message=str(ex)
                    )
                    raise ex
            return sync_wrapper
    return decorator
