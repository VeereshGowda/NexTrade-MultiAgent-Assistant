# 🚀 NexTrade - Quick Deployment Reference Card

## ⚡ One-Command Deployments

```bash
# Local Development
streamlit run streamlit_app.py

# Docker
docker-compose up -d

# Kubernetes
kubectl apply -f kubernetes.yaml

# Automated (Linux/macOS)
./deploy.sh deploy-docker

# Automated (Windows)
.\deploy.ps1 deploy-docker
```

---

## 📋 Essential Commands

### Docker
```bash
# Build
docker build -t nextrade:latest .

# Run
docker run -p 8501:8501 --env-file .env nextrade:latest

# Stop
docker stop $(docker ps -q --filter ancestor=nextrade:latest)
```

### Docker Compose
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Kubernetes
```bash
# Deploy
kubectl apply -f kubernetes.yaml

# Status
kubectl get pods -n nextrade

# Logs
kubectl logs -f deployment/nextrade-api -n nextrade

# Scale
kubectl scale deployment nextrade-api --replicas=3 -n nextrade

# Delete
kubectl delete -f kubernetes.yaml
```

---

## 🔑 Environment Variables

### Required
```bash
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
TAVILY_API_KEY=xxx
ALPHAVANTAGE_API_KEY=xxx
```

### Optional
```bash
LANGSMITH_API_KEY=xxx
GROQ_API_KEY=xxx
LOG_LEVEL=INFO
```

---

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit UI** | http://localhost:8501 | Web interface |
| **API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | Status |

---

## 🐛 Troubleshooting

### Check Logs
```bash
# Docker
docker logs <container_id>

# Docker Compose
docker-compose logs -f

# Kubernetes
kubectl logs -f <pod_name> -n nextrade
```

### Health Checks
```bash
# API
curl http://localhost:8000/health

# Full check
./deploy.sh health  # Linux/macOS
.\deploy.ps1 health  # Windows
```

### Common Issues

**API Keys Missing**
```bash
cp .env.example .env
# Edit .env with your keys
```

**Port Already in Use**
```bash
# Change ports in docker-compose.yml or .env
API_PORT=8001
UI_PORT=8502
```

**Database Locked**
```bash
# Stop all instances
docker-compose down
# Restart
docker-compose up -d
```

---

## 📖 Documentation Links

- **Quick Start**: [`Documentation/QUICK_START.md`](Documentation/QUICK_START.md)
- **Full Setup**: [`Documentation/SETUP.md`](Documentation/SETUP.md)
- **Licensing**: [`Documentation/LICENSING_AND_DEPLOYMENT.md`](Documentation/LICENSING_AND_DEPLOYMENT.md)
- **Improvements**: [`PRODUCTION_IMPROVEMENTS.md`](PRODUCTION_IMPROVEMENTS.md)

---

## 📞 Quick Support

- **Email**: vg@abc.com
- **Issues**: [GitHub](https://github.com/VeereshGowda/NexTrade-MultiAgent-Assistant/issues)

---

## ⚠️ Before Production

- [ ] Configure API keys in `.env`
- [ ] Enable guardrails
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review security settings
- [ ] Test HITL workflow

---

**© 2025 Veeresh Gowda | MIT License**
