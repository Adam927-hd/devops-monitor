# DevOps Monitoring Dashboard

Système de monitoring temps réel construit en Python, containerisé avec Docker, et déployé sur Azure via GitHub Actions.

## Architecture

```
GitHub Actions CI/CD
  ├── lint (flake8)
  ├── test (pytest --cov ≥ 75 %)
  ├── build & push → Azure Container Registry
  └── deploy → Azure Container Apps
        │
        ├── devops-monitor-api      (FastAPI  — port 8000)
        └── devops-monitor-dashboard (Streamlit — port 8501)
```

## Prérequis

- Python 3.11+
- Docker & Docker Compose
- Make (Windows : [chocolatey](https://chocolatey.org/) → `choco install make`)

## Lancement local (Docker)

```bash
cp .env.example .env   # remplir API_KEY
make up                # démarre la stack
make logs              # suivre les logs
make down              # arrêter la stack
```

- API : http://localhost:8000/docs
- Dashboard : http://localhost:8501

## Lancement local (sans Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/macOS

pip install -r requirements.txt

# Terminal 1 — API
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Dashboard
streamlit run dashboard/app.py
```

## Tests

```bash
make test              # pytest + coverage ≥ 75 %
make lint              # flake8
```

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `API_KEY` | `dev-secret-key` | Clé d'accès aux endpoints protégés |
| `API_BASE_URL` | `http://localhost:8000` | URL de l'API vue par le dashboard |

## API Endpoints

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/health` | — | Liveness probe |
| GET | `/metrics` | — | Snapshot CPU / mémoire / disque |
| WS | `/ws/metrics` | — | Stream JSON toutes les secondes |
| POST | `/servers` | clé | Enregistrer un serveur |
| GET | `/servers` | — | Lister les serveurs (`?status=UP`) |
| GET | `/servers/{id}` | — | Détail d'un serveur |
| DELETE | `/servers/{id}` | clé | Supprimer un serveur |
| POST | `/servers/{id}/check` | — | Déclencher un health check immédiat |

## Déploiement Azure

### Secrets GitHub à configurer

| Secret | Contenu |
|--------|---------|
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_CLIENT_SECRET` | App registration secret |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID |
| `ACR_NAME` | Nom du registry (sans `.azurecr.io`) |

### Provisionner l'infrastructure

```bash
az group create --name devops-monitor-rg --location westeurope

az acr create \
  --name <votre-acr> \
  --resource-group devops-monitor-rg \
  --sku Basic

az containerapp env create \
  --name devops-monitor-env \
  --resource-group devops-monitor-rg \
  --location westeurope
```

### URLs live

| Service | URL |
|---------|-----|
| API (health) | https://devops-monitor-gja9cdefezgfbmc8.francecentral-01.azurewebsites.net/health |
| API (docs) | https://devops-monitor-gja9cdefezgfbmc8.francecentral-01.azurewebsites.net/docs |

## Structure du dépôt

```
devops-monitor/
├── api/                  # Backend FastAPI
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── metrics.py
│   ├── poller.py
│   └── Dockerfile
├── dashboard/            # Frontend Streamlit
│   ├── app.py
│   └── Dockerfile
├── tests/
│   ├── test_metrics.py
│   ├── test_routes.py
│   └── test_poller.py
├── .github/workflows/
│   └── ci-cd.yml
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── setup.cfg
├── .env.example
└── README.md
```
