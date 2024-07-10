FROM python:3.8.19-slim

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python -m pip install rasa 
RUN pip install -r requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_md-3.7.0/pt_core_news_md-3.7.0.tar.gz

COPY . /app

RUN rasa train

USER root

EXPOSE 5005
EXPOSE 5055

ENTRYPOINT [ "rasa" ]

CMD ["run", "--enable-api", "--cors", "*"]
