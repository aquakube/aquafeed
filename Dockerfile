FROM node:14-slim as build_web

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN cd app && npm install && npm run build

RUN mkdir -p server/src/services/server/static \
    && cp -r app/build/* server/src/services/server/static \
    && cp -r server/src/services/server/static/static/* server/src/services/server/static \
    && cp app/public/favicon.png server/src/services/server/static/favicon.png \
    && rm -rf server/src/services/server/static/static \
    && rm -rf app



FROM python:3.11.1-slim

COPY --from=build_web /usr/src/app/server /usr/src/app/

WORKDIR /usr/src/app

RUN pip install --upgrade pip

RUN pip install pipenv

RUN pipenv lock && pipenv install --system --deploy

CMD [ "python3", "src/main.py" ]
