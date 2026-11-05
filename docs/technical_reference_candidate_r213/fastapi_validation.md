# FastAPI request validation
Source: https://fastapi.tiangolo.com/tutorial/handling-errors/

FastAPI raises RequestValidationError when request data fails validation. Its default handler returns a 422 response. Applications can override that handler. Review custom responses so they do not unnecessarily expose sensitive input.

A valid custom-handler example needs these imports:
    from fastapi import FastAPI, Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid request"},
        )
