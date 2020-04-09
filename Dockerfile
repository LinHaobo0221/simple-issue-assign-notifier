FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY ./config.ini /usr/src/app
COPY ./git-fetcher.py /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt


CMD [ "python", "-u", "./git-fetcher.py" ]
