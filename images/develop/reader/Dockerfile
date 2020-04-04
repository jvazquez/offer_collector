FROM python:3.7.6
COPY reader /app/reader
RUN pip install -r /app/reader/requirements.txt
WORKDIR /app/reader
CMD ["python", "listener.py"]