FROM python:3.12-slim as builder

WORKDIR /devlens-project

COPY . .

RUN python -m venv /venv
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -e .

COPY requirements.txt pyproject.toml ./

RUN pip install --no-cache-dir -e .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["devlens"]
CMD ["--help"]

