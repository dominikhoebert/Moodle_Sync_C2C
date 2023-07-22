FROM python:3.11-slim-buster

WORKDIR /c2c

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY *.py ./

ENTRYPOINT ["python3", "c2c.py"]
CMD ["--help"]