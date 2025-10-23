# GoQuant Matching Engine - Deployment Guide

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd GoQuant
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the server**:
```bash
python main.py
```

4. **Test the installation**:
```bash
python start.py test
```

## Development Setup

### Environment Setup

1. **Create virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install development dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run tests**:
```bash
python run_tests.py
```

4. **Start development server**:
```bash
python main.py
```

### Configuration

The matching engine can be configured through environment variables or by modifying `src/config.py`:

```bash
# Environment variables
export HOST=0.0.0.0
export PORT=8000
export DEBUG=True
export LOG_LEVEL=INFO
```

## Production Deployment

### Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

2. **Build and run**:
```bash
docker build -t goquant-matching-engine .
docker run -p 8000:8000 goquant-matching-engine
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  matching-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=False
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Systemd Service (Linux)

Create `/etc/systemd/system/goquant-matching-engine.service`:

```ini
[Unit]
Description=GoQuant Matching Engine
After=network.target

[Service]
Type=simple
User=goquant
WorkingDirectory=/opt/goquant
ExecStart=/opt/goquant/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable goquant-matching-engine
sudo systemctl start goquant-matching-engine
```

## Performance Tuning

### System Configuration

1. **CPU Affinity**:
```bash
# Bind to specific CPU cores
taskset -c 0,1 python main.py
```

2. **Memory Limits**:
```bash
# Set memory limits
ulimit -v 2097152  # 2GB virtual memory
```

3. **File Descriptors**:
```bash
# Increase file descriptor limit
ulimit -n 65536
```

### Application Configuration

Modify `src/config.py` for production:

```python
class Settings(BaseSettings):
    # Performance settings
    MAX_ORDERS_PER_SECOND: int = 50000
    BATCH_SIZE: int = 1000
    MAX_ORDER_BOOK_LEVELS: int = 10000
    
    # Memory settings
    MAX_ACTIVE_ORDERS: int = 1000000
    
    # Logging settings
    LOG_LEVEL: str = "WARNING"  # Reduce log verbosity
```

## Monitoring and Logging

### Log Configuration

The engine creates several log files:

- `matching_engine.log`: Main application log
- `trades.log`: Trade execution log (if configured)
- `errors.log`: Error log (if configured)

### Health Checks

The engine provides health check endpoints:

- `GET /health`: Basic health status
- `GET /`: Root endpoint with service info

### Metrics Collection

For production monitoring, consider integrating:

- **Prometheus**: For metrics collection
- **Grafana**: For visualization
- **ELK Stack**: For log aggregation

Example Prometheus metrics endpoint:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Add to main.py
ORDERS_PROCESSED = Counter('orders_processed_total', 'Total orders processed')
ORDER_LATENCY = Histogram('order_processing_seconds', 'Order processing time')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Security Considerations

### Network Security

1. **Firewall Configuration**:
```bash
# Allow only necessary ports
ufw allow 8000/tcp
ufw deny 22/tcp  # If not using SSH
```

2. **Reverse Proxy** (Nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Application Security

1. **Input Validation**: All inputs are validated
2. **Rate Limiting**: Implement rate limiting for production
3. **Authentication**: Add API key authentication
4. **HTTPS**: Use SSL/TLS in production

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Distribute traffic across multiple instances
2. **Shared State**: Use Redis for shared order book state
3. **Database**: Persist order book state to database

### Vertical Scaling

1. **CPU**: Use more powerful CPUs
2. **Memory**: Increase RAM for larger order books
3. **Storage**: Use SSD for better I/O performance

## Backup and Recovery

### Data Backup

1. **Order Book State**: Regular snapshots to persistent storage
2. **Trade History**: Export to external database
3. **Configuration**: Version control for configuration files

### Disaster Recovery

1. **Hot Standby**: Run secondary instance
2. **Data Replication**: Replicate critical data
3. **Failover**: Automatic failover mechanisms

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

2. **Memory Issues**:
```bash
# Check memory usage
ps aux | grep python
# Monitor memory
htop
```

3. **Performance Issues**:
```bash
# Profile the application
python -m cProfile main.py
# Monitor system resources
iostat -x 1
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python main.py
```

## Maintenance

### Regular Tasks

1. **Log Rotation**: Configure logrotate
2. **Health Monitoring**: Set up alerts
3. **Performance Monitoring**: Track key metrics
4. **Security Updates**: Keep dependencies updated

### Updates

1. **Code Updates**: Use blue-green deployment
2. **Dependency Updates**: Test thoroughly before production
3. **Configuration Changes**: Validate before applying

This deployment guide provides comprehensive instructions for deploying the GoQuant Matching Engine in various environments.
