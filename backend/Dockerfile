FROM python:3.12-slim

#set environment variables 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


# Install dependendances
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependences 
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


# Copy project 
COPY . /app/

RUN python manage.py collectstatic --noinput


# Create media 
RUN mkdir -p /app/media

EXPOSE 8000

# gunicorn 
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "mtl_app.wsgi:application"]

