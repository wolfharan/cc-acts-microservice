FROM alpine:3.7
ENV TEAM_ID=CC_128_133_171_177
EXPOSE 80

WORKDIR /app
RUN apk add python
RUN apk add py-pip
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY templates /app/templates

COPY acts_flask.py /app
CMD python acts_flask.py
