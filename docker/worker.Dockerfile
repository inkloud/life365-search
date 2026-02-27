FROM python:3.14.3
LABEL maintainer="Luca Bacchi <bacchilu@gmail.com> (https://github.com/bacchilu)"

ARG SUPERCRONIC_VERSION=v0.2.43
ARG TARGETARCH

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=appuser

RUN groupadd -g ${GROUP_ID} ${USERNAME}
RUN useradd -m -u ${USER_ID} -g ${USERNAME} ${USERNAME}

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install -r requirements.txt

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    case "${TARGETARCH:-amd64}" in \
      amd64) SUPERCRONIC_ARCH="amd64" ;; \
      arm64) SUPERCRONIC_ARCH="arm64" ;; \
      *) echo "Unsupported TARGETARCH: ${TARGETARCH}"; exit 1 ;; \
    esac; \
    curl -fsSLo /usr/local/bin/supercronic "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/supercronic-linux-${SUPERCRONIC_ARCH}"; \
    chmod +x /usr/local/bin/supercronic; \
    apt-get purge -y --auto-remove curl; \
    rm -rf /var/lib/apt/lists/*

COPY app /app/app
COPY worker /app/worker

RUN chown -R ${USERNAME}:${USERNAME} /app
USER ${USERNAME}

CMD ["celery", "-A", "app.infrastructure.celery.app.celery_app", "worker", "--loglevel=info"]