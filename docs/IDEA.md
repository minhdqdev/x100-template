

Anomaly Detection System là hệ thống phát hiện và cảnh báo dấu hiệu bất thường trong dữ liệu được gửi về từ các cảm biến IoT đo đạc trên các thiết bị công nghiệp. Hệ thống này sẽ phân tích dữ liệu thời gian thực từ các cảm biến để phát hiện các bất thường, gửi cảnh báo đến người dùng và cung cấp giao diện để quản lý và theo dõi các thiết bị.

## Functional Requirements
- Support được 100000 sensors, mỗi sensor gửi dữ liệu mỗi phút
- Phát hiện bất thường trong dữ liệu thời gian thực
- Gửi cảnh báo đến người dùng qua email, SMS, hoặc push notification trên web app
- Cung cấp giao diện web để quản lý và theo dõi các thiết bị

## Technologies
Architecture: Service-oriented architecture (SOA)

- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: Python, Django
  - Database: TimescaleDB (lưu trữ dữ liệu time-series) + Redis (để cache)
  - Celery, Kafka để xử lý các tác vụ nền và thông báo

- Containerization: Docker
- Lưu trữ source code trên Github private repo
