# Usage
# docker build -t mosazhaw/hikeplanner .
# docker run --name hikeplanner -e AZURE_STORAGE_CONNECTION_STRING='***' -p 9001:80 -d mosazhaw/hikeplanner

FROM python:3.13.7

# Install uv and dependencies
WORKDIR /usr/src/app
COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync --frozen --no-dev
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# Copy application files
COPY backend/app.py backend/app.py
COPY frontend/build frontend/build

# Docker Run Command
EXPOSE 80
ENV FLASK_APP=/usr/src/app/backend/app.py
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]
