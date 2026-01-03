# Breatheasy

A comprehensive air quality monitoring system with real-time sensor data visualization.

## Stack

**Frontend (Client)**
- React 18 with TypeScript
- Vite for build tooling and dev server
- TanStack Query for data fetching and caching
- Recharts for data visualization
- Tailwind CSS for styling
- Axios for API calls

**Backend (API)**
- Python 3.9+
- FastAPI for REST API and WebSocket support
- Uvicorn as ASGI server
- SQLite for data persistence
- Pydantic for data validation
- GPIO libraries for sensor/display control

## Quick Start

### Backend Setup
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

## Installation

See the [installation guide](docs/installation.md) for detailed setup instructions.

## Development

- Frontend: `cd client && npm run dev`
- Backend: `cd api && uvicorn app.main:app --reload`

## Deployment

For production deployment on Raspberry Pi, see the [deployment guide](docs/deployment.md).
