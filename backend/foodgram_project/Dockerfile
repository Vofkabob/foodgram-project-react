FROM python:3.7-slim
WORKDIR /app
COPY foodgram_project .
RUN pip3 install -r /app/requirements.txt --no-cache-dir
CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0:8000" ]