FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

RUN apt-get update
RUN apt-get install -y curl

RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt

ENV DAGSTER_HOME=/dagster_home
RUN mkdir -p $DAGSTER_HOME
WORKDIR $DAGSTER_HOME

ADD . $DAGSTER_HOME

RUN pip3 install common 

EXPOSE 3000

CMD ["python3"]
