FROM python:3.8-alpine

# Install dependencies
COPY requirements.txt pokespeare/
RUN apk add sqlite && pip install -r pokespeare/requirements.txt --no-cache-dir

# Install pokespeare
COPY . /pokespeare
RUN pip install pokespeare/ --no-cache-dir
WORKDIR pokespeare/

# Set to production config, can be easily tweaked by passing -e on docker run
ENV APP_CONFIG pokespeare.config.ProductionConfig

CMD python start.py
