FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
CMD ["python3.9", "./manage.py", "runserver"]