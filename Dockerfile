ARG PYTHON_VERSION=3.8

FROM python:$PYTHON_VERSION

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=1 \
    PYTHON_VERSION=$PYTHON_VERSION

RUN echo "Python version: " $PYTHON_VERSION

# add appuser
ARG USER=appuser
ARG HOME=/home/${USER}
RUN adduser --home ${HOME} --shell /usr/sbin/nologin --disabled-password --disabled-login --gecos "" ${USER}
RUN chown ${USER} ${HOME} && chmod -R u+w ${HOME}

# Install poetry
RUN python3 -m pip install py pip poetry --upgrade

# Change workdir
WORKDIR ${HOME}

# Copy files
COPY pyproject.toml poetry.lock poetry.toml ./

# Install depencies
RUN poetry config virtualenvs.create false --local && poetry install --only main --no-interaction --no-ansi

# Copy
COPY api/ ./api/
COPY monitora/ ./monitora/
COPY templates/ ./
COPY manage.py ./

# set gunicorn permission
RUN chmod u+x /usr/local/bin/gunicorn

# Change user
USER ${USER}

EXPOSE 8000

# Run app
# ${POETRY_CMD} -m gunicorn --reload monitora.asgi:application -k uvicorn.workers.UvicornWorker
# CMD ["gunicorn", "-m", "gunicorn.", "-b", "0.0.0.0:8000", "monitora.asgi:application"]
CMD ["python3", "manage.py", "runserver", "8000"]