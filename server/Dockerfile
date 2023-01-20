FROM python:3.9 as builder

WORKDIR /usr/src/websockets

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/websockets/wheels -r requirements.txt


FROM python:3.9

# installing netcat (nc) since we are using that to listen to postgres server in entrypoint.bat
RUN apt-get update && apt-get install -y --no-install-recommends netcat && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install dependencies
COPY --from=builder /usr/src/websockets/wheels /wheels
COPY --from=builder /usr/src/websockets/requirements.txt .
RUN pip install --no-cache /wheels/*

# set work directory
WORKDIR /usr/src/websockets/

COPY . .
