# See https://stackoverflow.com/a/54763270/14748231

FROM python:3.11

WORKDIR /app

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --without=dev --no-interaction --no-ansi --no-root

COPY . .
RUN poetry install --without=dev --no-interaction --no-ansi

CMD [ "make", "run" ]
