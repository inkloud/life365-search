FROM python:3.14.3
LABEL maintainer="Luca Bacchi <bacchilu@gmail.com> (https://github.com/bacchilu)"

RUN pip3 install poetry

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USERNAME=appuser

RUN groupadd -g ${GROUP_ID} ${USERNAME}
RUN useradd -m -u ${USER_ID} -g ${USERNAME} ${USERNAME}

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install -r requirements.txt

COPY app /app/app

RUN chown -R ${USERNAME}:${USERNAME} /app
USER ${USERNAME}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
