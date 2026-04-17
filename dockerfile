ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.10

FROM apache/airflow:slim-${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ENV AIRFLOW_HOME=/opt/airflow \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt /

RUN pip install --no-cache-dir --no-compile \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "apache-airflow-providers-postgres" \
    "apache-airflow-providers-celery" \
    -r /requirements.txt
