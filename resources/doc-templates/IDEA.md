<!-- Phần này freestyle thôi, sử dụng Github Copilot vừa nghĩ vừa viết rất nhanh. -->

## Công nghệ sẽ sử dụng
Architecture: Service-oriented architecture (SOA)
- Project đơn giản, ko có frontend thì xài monolithic (vd: browser extension)


- **Frontend**: Next.js, React, Tailwind CSS
  - Template nếu có? dẫn link đến template
- **Backend**: Python, Django
  - DB: thường là PostgreSQL + Redis
  - Có chạy background task ko? -> Celery, Kafka, RabbitMQ


### DevOps toolchain
<!-- Tuỳ chỉnh theo thực tế dự án -->

- CI/CD: GitHub Actions, GitLab CI
- Containerization: Docker
- Orchestration: Kubernetes
- Monitoring: Prometheus, Grafana
- Logging: ELK Stack (Elasticsearch, Logstash, Kibana)



## Domain

### Entities

For example:
- **User**: Represents a user in the system (Admin, Operator, Viewer)
- **Device**: Represents an IoT device with associated metadata (type, location, status)
- **SensorData**: Represents time-series data from IoT sensors (timestamp, value, device_id)
- **Alert**: Represents an anomaly detection alert (severity, status, timestamp, related_data)

### Relationships

For example:
- **User** can monitor multiple **Devices**
- **Device** generates multiple **SensorData** points
- **SensorData** can trigger multiple **Alerts**
- **User** can acknowledge or dismiss multiple **Alerts**
