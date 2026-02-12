FROM python:3.14.3
LABEL maintainer="Luca Bacchi <bacchilu@gmail.com> (https://github.com/bacchilu)"

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=appuser

RUN groupadd -g ${GROUP_ID} ${USERNAME}
RUN useradd -m -u ${USER_ID} -g ${USERNAME} ${USERNAME}

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY app /app/app
COPY worker /app/worker

RUN chown -R ${USERNAME}:${USERNAME} /app
USER ${USERNAME}

CMD ["celery", "-A", "app.infrastructure.celery.app.celery_app", "worker", "--loglevel=info"]