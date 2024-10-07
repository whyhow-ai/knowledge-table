FROM python:3.10-slim

RUN apt-get -y update

RUN pip install --no-cache-dir --upgrade pip
COPY ./ /code
RUN pip install --no-cache-dir /code
RUN rm -rf /code

# Change working directory since uvicorn does not allow for paths with `.` inside
WORKDIR /usr/local/lib/python3.10

EXPOSE 8000
ENTRYPOINT uvicorn $(knowledge-table-locate) --host 0.0.0.0 --port 8000
