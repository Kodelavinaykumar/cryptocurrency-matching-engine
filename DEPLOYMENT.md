# GoQuant Matching Engine - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the GoQuant Matching Engine in various environments, from development to production.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows
- **Python**: 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for production)
- **CPU**: Multi-core processor (4+ cores recommended)
- **Storage**: 10GB+ available disk space
- **Network**: Stable internet connection

### Software Dependencies

- **Python 3.11+**
- **pip** (Python package manager)
- **Docker** (optional, for containerized deployment)
- **Docker Compose** (optional, for multi-container deployment)
- **Kubernetes** (optional, for orchestrated deployment)

## Development Deployment

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GoQuant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**
   ```bash
   python main.py
   ```

5. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

### VS Code Development

1. **Open in VS Code**
   ```bash
   code .
   ```

2. **Use provided configurations**
   - Press `F5` to start debugging
   - Use `Ctrl+Shift+P` → "Tasks: Run Task" for various operations
   - Use the integrated terminal for command-line operations

## Docker Deployment

### Single Container Deployment

1. **Build the Docker image**
   ```bash
   docker build -t giquant-engine .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 giquant-engine
   ```

3. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

### Docker Compose Deployment

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     giquant-engine:
       build: .
       ports:
         - "8000:8000"
       environment:
         - HOST=0.0.0.0
         - PORT=8000
         - DEBUG=false
       volumes:
         - ./logs:/app/logs
       restart: unless-stopped
   
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
       restart: unless-stopped
   
     postgres:
       image: postgres:15-alpine
       environment:
         - POSTGRES_DB=giquant
         - POSTGRES_USER=giquant
         - POSTGRES_PASSWORD=password
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
       restart: unless-stopped
   
   volumes:
     redis_data:
     postgres_data:
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Verify deployment**
   ```bash
   curl http://localhost:8000/health
   ```

## Production Deployment

### Environment Configuration

1. **Create production environment file**
   ```bash
   # .env.production
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   LOG_LEVEL=INFO
   MAX_ORDERS_PER_SECOND=10000
   ORDER_BOOK_DEPTH=100
   
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/giquant
   REDIS_URL=redis://localhost:6379
   
   # Security
   JWT_SECRET_KEY=your-secret-key
   RATE_LIMIT_PER_MINUTE=1000
   ```

2. **Set environment variables**
   ```bash
   export $(cat .env.production | xargs)
   ```

### System Service Deployment

1. **Create systemd service file**
   ```ini
   # /etc/systemd/system/giquant-engine.service
   [Unit]
   Description=GoQuant Matching Engine
   After=network.target
   
   [Service]
   Type=simple
   User=giquant
   WorkingDirectory=/opt/giquant
   Environment=PATH=/opt/giquant/venv/bin
   ExecStart=/opt/giquant/venv/bin/python main.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service**
   ```bash
   sudo systemctl enable giquant-engine
   sudo systemctl start giquant-engine
   sudo systemctl status giquant-engine
   ```

### Load Balancer Configuration

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/giquant
upstream giquant_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.giquant.com;
    
    location / {
        proxy_pass http://giquant_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
        proxy_pass http://giquant_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### HAProxy Configuration

```haproxy
# /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend giquant_frontend
    bind *:80
    default_backend giquant_backend

backend giquant_backend
    balance roundrobin
    server giquant1 127.0.0.1:8000 check
    server giquant2 127.0.0.1:8001 check
    server giquant3 127.0.0.1:8002 check
```

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: giquant
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: giquant-config
  namespace: giquant
data:
  HOST: "0.0.0.0"
  PORT: "8000"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
```

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: giquant-engine
  namespace: giquant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: giquant-engine
  template:
    metadata:
      labels:
        app: giquant-engine
    spec:
      containers:
      - name: giquant-engine
        image: giquant-engine:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: giquant-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: giquant-service
  namespace: giquant
spec:
  selector:
    app: giquant-engine
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: giquant-hpa
  namespace: giquant
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: giquant-engine
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Verify deployment
kubectl get pods -n giquant
kubectl get services -n giquant
```

## Cloud Deployment

### AWS Deployment

#### ECS (Elastic Container Service)

1. **Create ECS cluster**
   ```bash
   aws ecs create-cluster --cluster-name giquant-cluster
   ```

2. **Create task definition**
   ```json
   {
     "family": "giquant-engine",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "giquant-engine",
         "image": "your-account.dkr.ecr.region.amazonaws.com/giquant-engine:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "HOST",
             "value": "0.0.0.0"
           },
           {
             "name": "PORT",
             "value": "8000"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/giquant-engine",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

3. **Create service**
   ```bash
   aws ecs create-service \
     --cluster giquant-cluster \
     --service-name giquant-service \
     --task-definition giquant-engine:1 \
     --desired-count 3 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

#### EKS (Elastic Kubernetes Service)

1. **Create EKS cluster**
   ```bash
   eksctl create cluster --name giquant-cluster --region us-west-2 --nodegroup-name workers --node-type t3.medium --nodes 3
   ```

2. **Deploy using Kubernetes manifests**
   ```bash
   kubectl apply -f k8s/
   ```

### Google Cloud Platform

#### Google Kubernetes Engine (GKE)

1. **Create GKE cluster**
   ```bash
   gcloud container clusters create giquant-cluster \
     --zone us-central1-a \
     --num-nodes 3 \
     --machine-type e2-medium
   ```

2. **Deploy application**
   ```bash
   kubectl apply -f k8s/
   ```

### Azure

#### Azure Kubernetes Service (AKS)

1. **Create AKS cluster**
   ```bash
   az aks create \
     --resource-group giquant-rg \
     --name giquant-cluster \
     --node-count 3 \
     --node-vm-size Standard_B2s \
     --generate-ssh-keys
   ```

2. **Deploy application**
   ```bash
   kubectl apply -f k8s/
   ```

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'giquant-engine'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "GoQuant Matching Engine",
    "panels": [
      {
        "title": "Orders Per Second",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(giquant_orders_total[5m])",
            "legendFormat": "Orders/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(giquant_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Log Aggregation

#### ELK Stack (Elasticsearch, Logstash, Kibana)

1. **Logstash configuration**
   ```ruby
   # logstash.conf
   input {
     file {
       path => "/var/log/giquant/*.log"
       type => "giquant"
     }
   }
   
   filter {
     if [type] == "giquant" {
       grok {
         match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} - %{WORD:logger} - %{LOGLEVEL:level} - %{GREEDYDATA:message}" }
       }
       date {
         match => [ "timestamp", "ISO8601" ]
       }
     }
   }
   
   output {
     elasticsearch {
       hosts => ["localhost:9200"]
       index => "giquant-%{+YYYY.MM.dd}"
     }
   }
   ```

2. **Kibana dashboard**
   - Create index pattern: `giquant-*`
   - Create visualizations for logs
   - Set up alerts for errors

## Security Considerations

### SSL/TLS Configuration

#### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name api.giquant.com;
    
    ssl_certificate /etc/ssl/certs/giquant.crt;
    ssl_certificate_key /etc/ssl/private/giquant.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://giquant_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

### Authentication and Authorization

1. **JWT Configuration**
   ```python
   # src/security/jwt.py
   import jwt
   from datetime import datetime, timedelta
   
   def create_access_token(data: dict):
       to_encode = data.copy()
       expire = datetime.utcnow() + timedelta(hours=24)
       to_encode.update({"exp": expire})
       encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
       return encoded_jwt
   ```

2. **Rate Limiting**
   ```python
   # src/middleware/rate_limit.py
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   
   @app.post("/api/v1/orders")
   @limiter.limit("100/minute")
   async def submit_order(request: Request, ...):
       # Order submission logic
   ```

## Performance Tuning

### System Optimization

1. **Kernel parameters**
   ```bash
   # /etc/sysctl.conf
   net.core.somaxconn = 65535
   net.core.netdev_max_backlog = 5000
   net.ipv4.tcp_max_syn_backlog = 65535
   net.ipv4.tcp_keepalive_time = 600
   net.ipv4.tcp_keepalive_intvl = 60
   net.ipv4.tcp_keepalive_probes = 10
   ```

2. **File descriptor limits**
   ```bash
   # /etc/security/limits.conf
   * soft nofile 65535
   * hard nofile 65535
   ```

### Application Optimization

1. **Worker processes**
   ```bash
   # Use multiple workers
   uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. **Connection pooling**
   ```python
   # src/database/pool.py
   from sqlalchemy.pool import QueuePool
   
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U giquant -d giquant > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/var/backups/giquant"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U giquant -d giquant > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /etc/nginx/sites-available/giquant \
  /etc/systemd/system/giquant-engine.service \
  /opt/giquant/.env.production
```

## Disaster Recovery

### High Availability Setup

1. **Multi-region deployment**
   - Deploy in multiple availability zones
   - Use database replication
   - Implement failover mechanisms

2. **Backup and restore procedures**
   - Regular database backups
   - Configuration backups
   - Application state backups

### Recovery Procedures

1. **Service recovery**
   ```bash
   # Restart service
   sudo systemctl restart giquant-engine
   
   # Check service status
   sudo systemctl status giquant-engine
   
   # View logs
   sudo journalctl -u giquant-engine -f
   ```

2. **Database recovery**
   ```bash
   # Restore from backup
   psql -h localhost -U giquant -d giquant < backup_20231022_120000.sql
   ```

## Maintenance

### Regular Maintenance Tasks

1. **Log rotation**
   ```bash
   # /etc/logrotate.d/giquant
   /var/log/giquant/*.log {
       daily
       missingok
       rotate 30
       compress
       delaycompress
       notifempty
       create 644 giquant giquant
       postrotate
           systemctl reload giquant-engine
       endscript
   }
   ```

2. **Health checks**
   ```bash
   # Health check script
   #!/bin/bash
   response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
   if [ $response != "200" ]; then
       echo "Health check failed: $response"
       systemctl restart giquant-engine
   fi
   ```

3. **Performance monitoring**
   ```bash
   # Monitor system resources
   top -p $(pgrep -f "python main.py")
   
   # Monitor network connections
   netstat -an | grep :8000
   
   # Monitor disk usage
   df -h
   ```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u giquant-engine -n 50
   
   # Check configuration
   python -c "import src.config; print(src.config.settings)"
   
   # Test dependencies
   python -c "import fastapi, uvicorn, websockets"
   ```

2. **High memory usage**
   ```bash
   # Monitor memory usage
   ps aux | grep python
   
   # Check for memory leaks
   python -m memory_profiler main.py
   ```

3. **Connection issues**
   ```bash
   # Check port availability
   netstat -tlnp | grep :8000
   
   # Test connectivity
   telnet localhost 8000
   
   # Check firewall
   sudo ufw status
   ```

### Performance Issues

1. **Slow response times**
   - Check CPU usage
   - Monitor memory usage
   - Review database performance
   - Check network latency

2. **High error rates**
   - Review application logs
   - Check system resources
   - Verify configuration
   - Test dependencies

## Conclusion

This deployment guide provides comprehensive instructions for deploying the GoQuant Matching Engine in various environments. The system is designed to be highly scalable, reliable, and maintainable, with support for both traditional and cloud-native deployment patterns.

For additional support or questions, refer to the project documentation or contact the development team.
