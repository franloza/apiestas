FROM python:3.6 as build

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip install pipenv

WORKDIR /build
COPY Pipfile Pipfile.lock /build/
RUN bash -c 'PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile --dev'

FROM python:3.6-slim as app

COPY --from=build /build /build
ENV PATH="/build/.venv/bin:$PATH"
WORKDIR /usr/src/app
ADD . /usr/src/app

ENTRYPOINT ["python", "main.py"]



