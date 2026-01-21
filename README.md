# HikePlanner

inspired by https://blog.mimacom.com/data-collection-scrapy-hiketime-prediction/
similar dataset 

## Data

* https://www.kaggle.com/datasets/roccoli/gpx-hike-tracks

## Azure Blob Storage

* Save model to Azure Blob Storage
* Always save new version of model
* Zugriff: Speicherkonto > Zugriffsschlüssel
    * Als Umgebungsvariable für Docker
    * Als Secret für GitHub

## GitHub Action

* Scrape
* Load data to MongoDB (Azure Cosmos DB)
* Update model and save to Azure Blob Storage

## App
* Backend: Python Flask (backend/app.py)
* Frontend: SvelteKit (build still manually)

## Deployment with Docker

* Dockerfile
* Install dependencies with pip
* Copy Frontend (prebuilt, TODO Build)
* Azure Blob Storage: Zugriffsschlüssel als Umgebungsvariable

## Installation

* pyenv local 3.13.7
* uv venv .venv
* uv sync

## Ideas

* Personalized Model
    * For a specific Hikr user
    * z.B. 100 weitere "neue" Daten eines bestimmten Benutzers 
