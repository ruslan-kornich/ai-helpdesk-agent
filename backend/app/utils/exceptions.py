import functools
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class BusinessError(ApplicationError):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message, status_code)


async def business_exception_handler(request: Request, exception: BusinessError) -> JSONResponse:
    logger.warning(
        "BusinessError on {path}: {message}", path=request.url.path, message=exception.message
    )
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.message},
    )


def catch_errors[**ParamsType, ReturnType](
    func: Callable[ParamsType, Awaitable[ReturnType]],
) -> Callable[ParamsType, Awaitable[ReturnType | None]]:
    @functools.wraps(func)
    async def wrapper(*args: ParamsType.args, **kwargs: ParamsType.kwargs) -> ReturnType | None:
        try:
            return await func(*args, **kwargs)
        except BusinessError:
            raise
        except Exception as error:
            logger.exception("Unhandled error in {name}: {error}", name=func.__name__, error=error)
            return None

    return wrapper
