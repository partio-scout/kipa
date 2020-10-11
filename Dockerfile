FROM python:2

WORKDIR /app/web

COPY . /app/

RUN echo "PYTHONPATH=/usr/local/lib/python2.7/site-packages" | tee -a /etc/profile

ENTRYPOINT ["/app/docker-entrypoint.sh"]

EXPOSE 3000

CMD ["./manage.py", "runserver", "0.0.0.0:3000"]

RUN pip install -r /app/requirements.txt
