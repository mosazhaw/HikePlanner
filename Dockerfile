# Usage
# docker build -t mosazhaw/hikeplanner .
# docker run --name hikeplanner -e AZURE_STORAGE_CONNECTION_STRING='***' -p 9001:80 -d mosazhaw/hikeplanner

FROM python:3.13.7

# Copy Files
WORKDIR /usr/src/app
COPY backend/app.py backend/app.py
COPY frontend/build frontend/build

# Install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Docker Run Command
EXPOSE 80
ENV FLASK_APP=/usr/src/app/backend/app.py
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]