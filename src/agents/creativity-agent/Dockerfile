ARG BASE_IMAGE=rayproject/ray:2.9.3-py310

FROM ${BASE_IMAGE} as builder
USER root
RUN pip install --upgrade pip && \
    pip install poetry==1.7.1 poetry-plugin-export==1.6.0 && \
    poetry config virtualenvs.create false
WORKDIR /build
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --without-hashes --without dev --output requirements.txt

FROM ${BASE_IMAGE}
WORKDIR /serve_app
COPY --from=builder /build/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt
COPY src/creativity_agent /serve_app/creativity_agent
EXPOSE 8000
ENTRYPOINT ["serve", "run", "creativity_agent.ray_entrypoint:agent_builder", "--host=0.0.0.0", "--port=8000"]
