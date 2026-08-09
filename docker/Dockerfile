FROM python:3.11-slim

LABEL org.extrudely.component="cad-sandbox"
LABEL description="Isolated CAD execution environment for CadQuery/OCP"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libsm6 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir cadquery>=2.5

RUN useradd --create-home --shell /bin/bash caduser && \
    mkdir -p /workspace /sandbox && \
    chown caduser:caduser /workspace /sandbox

COPY --chown=caduser:caduser sandbox/ /sandbox/

ENV CADQUERY_SANDBOX=1
ENV CADQUERY_TIMEOUT=60

USER caduser
WORKDIR /workspace
VOLUME ["/workspace", "/sandbox"]

CMD ["python", "-c", "import cadquery; print('CadQuery ready:', cadquery.__version__)"]
