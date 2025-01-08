# based on the uv's example image

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y libpq5 libpq-dev

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


ADD ./intbot /app/intbot
ADD ./README.md /app
ADD ./Makefile /app
ADD ./pyproject.toml /app
ADD ./uv.lock /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then from builder build the production image
# It needs the very same version of python/base image.
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y make libpq5

RUN adduser --disabled-password app

COPY --from=builder --chown=app:app /app /app

USER app

WORKDIR /app

ENV PATH="/app/.venv/bin/:$PATH"

RUN make in-container/collectstatic

EXPOSE 4672

# Run the django app by default
CMD ["make", "in-container/gunicorn"]
