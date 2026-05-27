from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.db.init_db import init_seed_data
from app.db.session import Base, SessionLocal, engine
from app.models import database  # noqa: F401


FIELD_ERROR_MESSAGES = {
    "o_ti_complex_g_hartree": "缺少 O→Ti complex 的自由能，无法计算 ΔGpoison。",
    "pi_complex_g_hartree": "缺少 π-complex 的自由能，无法计算 ΔGpoison。",
    "ts_g_hartree": "缺少 TS 或参考态自由能，无法计算 ΔG‡。",
    "free_site_monomer_g_hartree": "缺少 TS 或参考态自由能，无法计算 ΔG‡。",
    "complex_g_hartree": "缺少络合物自由能，无法计算 ΔGbind。",
    "fragment_g_hartree": "缺少片段自由能，无法计算 ΔGbind。",
    "text": "当前 Gaussian 文本为空或缺失，无法解析。",
}


def _validation_detail(exc: RequestValidationError) -> dict:
    messages: list[str] = []
    for error in exc.errors():
        loc = error.get("loc", ())
        field = str(loc[-1]) if loc else ""
        message = FIELD_ERROR_MESSAGES.get(field, f"字段 {field or 'unknown'} 校验失败：{error.get('msg', '输入无效')}")
        if message not in messages:
            messages.append(message)
    return {
        "detail": "；".join(messages) if messages else "请求参数校验失败。",
        "errors": exc.errors(),
        "language": "zh-CN",
    }


def create_app() -> FastAPI:
    settings = get_settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        init_seed_data(db)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Quantum-chemical workflow API for Si-O bonds, TEA interactions, Ti-site poisoning, "
            "and Ziegler-Natta insertion pathways. The API parses uploaded files but never executes Gaussian."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=jsonable_encoder(_validation_detail(exc)))

    app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
