# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the x100-template - a master repository template that manages full-stack applications using Git submodules. It serves as a container for both frontend and backend submodules, specifically an Anomaly Detection System (ADS) with Django REST Framework backend and Next.js frontend.

## Repository Structure

This is a master repository that contains:
- **submodules/backend**: Django-based ADS backend (anomaly detection system)
- **submodules/frontend**: Next.js-based ADS frontend
- **doc-templates/**: Documentation templates for projects
- **prompts/**: Best practices and development guidelines

## Common Commands

### Repository Management
```bash
# Clone with submodules
git clone --recursive <repo-url>

# Initialize submodules after cloning
git submodule update --init --recursive

# Update all submodules
git submodule update --remote

# Add new submodule
git submodule add -b <branch_name> <repo_url> submodules/<submodule_name>
```

### Frontend Development (Next.js)
Navigate to `submodules/frontend/` and run:
```bash
# Install dependencies (use --force due to React 19)
npm install --force

# Development server with Turbopack
PORT=30101 npm run dev

# Build and production
npm run build
PORT=23101 npm run start

# Code quality
npm run lint
npm run format
```

### Backend Development (Django)
Navigate to `submodules/backend/` and run:
```bash
# Setup development environment
mkdir -p data/docker-storage/grafana
sudo chown -R 472:472 data/docker-storage/grafana
docker compose -f docker/docker-compose.yaml up -d

# Django development (inside src/backend/)
cd src/backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py test

# ML model training
python manage.py train_indicator <indicator_id>

# Background processing
python manage.py process_sensor_reading --workers=4
python manage.py persist_sensor_reading --workers=1
```

## Architecture Overview

### Master Repository Pattern
- Uses Git submodules to manage multiple related repositories
- Each submodule (frontend/backend) has its own development lifecycle
- Centralized configuration and documentation in master repository

### Frontend Architecture (Next.js 15.3)
- **Tech Stack**: React 19, TypeScript, Tailwind CSS 4.x, ReUI components
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js + custom JWT flow
- **State Management**: TanStack React Query
- **Multiple Demo Layouts**: Switch between Demo1Layout to Demo5Layout

### Backend Architecture (Django)
- **Tech Stack**: Django 5.2, DRF, TimescaleDB, Celery, Redis, Kafka
- **ML Models**: Isolation Forest, SARIMA, LSTM for anomaly detection
- **Time-series**: TimescaleDB for efficient sensor data storage
- **Architecture**: Service-oriented with dedicated service classes

## Development Workflow

### Working with Submodules
1. Navigate to specific submodule directory for development
2. Each submodule has its own CLAUDE.md with detailed instructions
3. Commit changes in submodule first, then update master repository
4. Use branch strategies: develop branches in submodules

### Project Setup Process
1. Clone repository with `--recursive` flag
2. Setup backend: Docker services → Django migrations → superuser
3. Setup frontend: npm install → database setup → development server
4. Refer to individual submodule CLAUDE.md files for detailed setup

### Adding New Features
1. Determine if feature belongs to frontend, backend, or both
2. Navigate to appropriate submodule directory
3. Follow the detailed development guidelines in submodule's CLAUDE.md
4. Update master repository after submodule changes

## Environment Configuration

### Backend Services (Docker)
- API Server: http://localhost:30100
- PostgreSQL/TimescaleDB: Port 5432
- Redis: Port 6379
- Grafana: http://localhost:30102
- RabbitMQ Management: http://localhost:15672
- Kafka: Port 9092

### Frontend Services
- Development server: http://localhost:3000 (default Next.js port)
- Production build with optimized assets

## Important Notes

### Git Submodule Considerations
- Always work within submodule directories for code changes
- Submodules track specific commits, not branches
- Update master repository when submodule commits change
- Use `git submodule update --remote` to fetch latest submodule changes

### Development Best Practices
From `prompts/BEST_PRACTICES.md`:
1. Context engineering > Prompt engineering
2. Use Claude Code (Claude Sonnet 4) for coding assistant
3. Use GitHub Copilot for code auto completions
4. Use ChatGPT for planning
5. Use Gemini if Claude Code doesn't solve your problem

### Documentation Templates
- `doc-templates/PROJECT_CONTEXT.template.md` provides project context template
- Each submodule maintains its own comprehensive documentation

### Dependencies Management
- Frontend: Use `npm install --force` due to React 19 compatibility
- Backend: Use `uv` package manager instead of pip (Python 3.12+ required)

## Security and Performance
- JWT-based authentication across frontend/backend
- Organization-based data isolation (multi-tenant)
- TimescaleDB optimizations for time-series data
- Redis caching and background processing with Celery
- Comprehensive monitoring with Grafana dashboards