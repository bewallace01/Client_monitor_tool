# 📊 Client Intelligence Monitor

> **Modern client intelligence platform with FastAPI backend and React frontend for monitoring news, events, and business updates**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a67e.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178c6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Client Intelligence Monitor is a powerful, production-ready application designed for **Account Managers**, **Customer Success Teams**, and **Business Development professionals** who need to stay informed about their clients' activities, news, and business developments.

---

## 🌟 Key Features

### 🎯 Smart Monitoring
- **Automated News Collection**: Continuously scans multiple sources for client news
- **Intelligent Classification**: Automatically categorizes events (funding, acquisitions, product launches, etc.)
- **Relevance Scoring**: Prioritizes events based on importance and relevance
- **Real-time Updates**: Stay informed with the latest client developments

### 📊 Modern Dashboard
- **React Frontend**: Fast, responsive UI built with React + TypeScript
- **Visual Analytics**: Interactive charts with Recharts
- **Activity Tracking**: Monitor event trends across your portfolio
- **RESTful API**: FastAPI backend with OpenAPI documentation

### 🔔 Smart Notifications
- **Rule-Based Alerts**: Create custom notification rules
- **Email Digests**: Daily/weekly summaries of important events
- **Priority Filtering**: Focus on what matters most
- **User Interactions**: Track reads, stars, and notes on events

### 🛠️ Production-Ready
- **Modern Stack**: FastAPI + React + PostgreSQL/SQLite
- **Authentication**: JWT-based user authentication
- **Multi-tenant**: Support for multiple businesses/organizations
- **Docker Support**: Containerized deployment ready
- **API Documentation**: Interactive API docs with Swagger UI
- **Full Documentation**: Setup guides, API docs, deployment guides

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **(Optional) PostgreSQL**: 15.x or higher
- **(Optional) Redis**: 7.x or higher

### Installation (5 Steps)

```bash
# 1. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
copy .env.example .env

# 2. Database Setup
alembic upgrade head

# 3. Create Admin User (Optional)
python scripts/create_admin.py

# 4. Frontend Setup (new terminal)
cd frontend
npm install
copy .env.example .env

# 5. Start Services
# Terminal 1 - Backend:
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend:
cd frontend
npm run dev
```

**Access the application:**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Quick Start

```bash
# Start all services with Docker Compose
docker compose up -d postgres redis

# Run migrations
docker compose exec backend alembic upgrade head

# Start application
docker compose --profile full up -d
```

For detailed setup instructions, see **[SETUP.md](SETUP.md)**

---

## 📸 Screenshots

### Dashboard Overview
*Main dashboard showing portfolio metrics, event timeline, and activity breakdown*

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Client Intelligence Monitor                             │
├─────────────────────────────────────────────────────────────┤
│  [52 Clients]  [184 Events]  [12 This Week]  [0.78 Avg]   │
│                                                              │
│  📈 Event Timeline (Last 30 Days)                           │
│  ████▀▀██▀▀███████▀▀▀▀████████▀▀▀███                        │
│                                                              │
│  📊 Events by Type        👥 Top Active Clients            │
│  ┌──────────────┐        ┌──────────────────┐             │
│  │ 💰 Funding   │        │ Acme Corp    █████│             │
│  │ 🤝 Partnership│       │ TechStart   ████  │             │
│  │ 🚀 Product    │       │ GlobalFinance ███ │             │
│  └──────────────┘        └──────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### Client Management
*Organize and track your client portfolio with detailed profiles*

### Event Monitoring
*Browse, filter, and analyze events across all clients*

### Global Search
*Unified search across clients and events with relevance ranking*

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│              (Interactive Dashboard)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│              Business Logic Layer                       │
│  ┌────────────┐  ┌──────────┐  ┌──────────────┐       │
│  │ Collectors │  │Processors│  │  Scheduler   │       │
│  │ (APIs)     │  │(AI Logic)│  │  (Automation)│       │
│  └────────────┘  └──────────┘  └──────────────┘       │
└───────────────────┬─────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────┐
│              SQLite Database                            │
│        (Clients, Events, Cache, Rules)                  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
News Sources → Collectors → Processors → Storage → UI
                              ↓
                      (Classify, Score, Dedupe)
                              ↓
                      Notification Engine
                              ↓
                          Email/Alerts
```

---

## 💻 Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 18.3 + TypeScript | Modern SPA with type safety |
| **UI Framework** | Vite 5.4 | Fast build tool and dev server |
| **Styling** | TailwindCSS 3.4 | Utility-first CSS framework |
| **State Management** | TanStack Query 5.x | Server state management |
| **Backend** | FastAPI 0.104 | High-performance async API |
| **ORM** | SQLAlchemy 2.0 | Database abstraction layer |
| **Database** | PostgreSQL 15 / SQLite | Relational data storage |
| **Cache** | Redis 7 | Optional caching layer |
| **Migrations** | Alembic 1.12 | Database version control |
| **Authentication** | JWT + Passlib | Secure user authentication |

### Key Libraries

#### Backend
- **pydantic** - Data validation & settings
- **uvicorn** - ASGI server
- **python-jose** - JWT tokens
- **httpx** - Async HTTP client

#### Frontend
- **axios** - HTTP client
- **react-router-dom** - Client-side routing
- **recharts** - Data visualization
- **react-hot-toast** - Notifications

### Design Patterns

- **Repository Pattern** - Clean data access layer
- **Factory Pattern** - Flexible collector creation
- **DTO Pattern** - Type-safe data transfer with Pydantic
- **Dependency Injection** - FastAPI's DI system
- **Component Composition** - React component architecture

---

## 📁 Project Structure

```
Client Monitor/
│
├── backend/                   # 🚀 FastAPI Backend
│   ├── alembic/              # Database migrations
│   │   ├── versions/         # Migration files
│   │   └── env.py           # Alembic environment
│   ├── app/                  # Application code
│   │   ├── api/             # API routes & endpoints
│   │   ├── core/            # Core functionality (config, security)
│   │   ├── database/        # Database connection
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── main.py          # FastAPI application
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Backend tests
│   ├── data/                # SQLite database (if used)
│   └── requirements.txt     # Python dependencies
│
├── frontend/                  # ⚛️ React Frontend
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   ├── utils/          # Utility functions
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── tailwind.config.js  # Tailwind configuration
│   └── vite.config.ts      # Vite configuration
│
├── archive/                   # 📦 Legacy files (archived)
│   ├── legacy-streamlit/    # Old Streamlit app
│   ├── old-scripts/         # Deprecated scripts
│   └── old-docs/            # Outdated documentation
│
├── docs/                      # 📚 Documentation
│   ├── USER_GUIDE.md        # End-user guide
│   ├── DEVELOPER_GUIDE.md   # Technical docs
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── API_SETUP.md         # API configuration
│
├── tests/                     # ✅ Integration tests
│
├── docker-compose.yml         # 🐳 Docker orchestration
├── .env.example              # Environment template
├── README.md                 # Project overview
└── SETUP.md                  # Detailed setup guide
```

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description | Audience |
|----------|-------------|----------|
| **[SETUP.md](SETUP.md)** | Complete installation & setup guide | Everyone |
| **[User Guide](docs/USER_GUIDE.md)** | Complete end-user documentation | End Users |
| **[Developer Guide](docs/DEVELOPER_GUIDE.md)** | Architecture & development guide | Developers |
| **[Deployment Guide](docs/DEPLOYMENT.md)** | Production deployment | DevOps |
| **[API Setup Guide](docs/API_SETUP.md)** | Configure external APIs | Administrators |

### Quick Links

- **Getting Started**: See **[SETUP.md](SETUP.md)** for detailed installation instructions
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Adding Features**: See [Developer Guide](docs/DEVELOPER_GUIDE.md#adding-new-features)
- **API Configuration**: See [API Setup Guide](docs/API_SETUP.md)
- **Legacy Files**: See [archive/README.md](archive/README.md) for archived Streamlit app

---

## 🎯 Use Cases

### Account Managers
- **Stay Informed**: Track all client news in one place
- **Proactive Outreach**: Engage clients based on their news
- **Portfolio Health**: Monitor trends across entire book of business

### Customer Success Teams
- **Risk Detection**: Early warning of client challenges
- **Expansion Opportunities**: Identify growth signals
- **Relationship Intelligence**: Better understand client context

### Business Development
- **Prospect Research**: Track potential client activity
- **Competitive Intelligence**: Monitor competitor moves
- **Market Trends**: Identify industry patterns

### Sales Teams
- **Warm Introductions**: Find relevant conversation starters
- **Deal Signals**: Spot buying indicators (funding, expansion)
- **Account Preparation**: Research before meetings

---

## 🚀 Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Core data models and storage
- [x] Basic UI with Streamlit
- [x] Mock APIs for testing
- [x] Client and event management
- [x] Dashboard with visualizations

### ✅ Phase 2: Intelligence (Complete)
- [x] Event classification
- [x] Relevance scoring
- [x] Deduplication
- [x] Advanced filtering
- [x] Global search

### ✅ Phase 3: Automation (Complete)
- [x] Scheduled scanning
- [x] Notification rules
- [x] Email alerts
- [x] API integrations (Google, NewsAPI)

### ✅ Phase 4: Polish & Testing (Complete)
- [x] Professional UI with design system
- [x] Comprehensive test suite (170+ tests)
- [x] Complete documentation
- [x] Demo mode
- [x] System testing page

### 🔄 Phase 5: Production Deployment (In Progress)
- [x] Docker containerization
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] CI/CD pipeline
- [ ] Monitoring & logging
- [ ] Performance optimization

### 📋 Phase 6: Advanced Features (Planned)
- [ ] Multi-user support
- [ ] Team collaboration
- [ ] Advanced analytics
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Mobile-responsive design
- [ ] Dark mode
- [ ] Custom event types
- [ ] API for external integrations

---

## 🧪 Testing

### Test Coverage

- **170+ Test Cases**
- **80%+ Code Coverage**
- **Unit Tests**: Models, Storage, Collectors, Processors
- **Integration Tests**: End-to-end workflows

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest -m unit            # Unit tests only
pytest -m integration     # Integration tests only
```

See [Testing Guide](docs/TESTING.md) for complete testing documentation.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application Mode
DEMO_MODE=false              # Set to true for demo data

# Database
DATABASE_PATH=data/client_intelligence.db

# API Configuration (Optional)
GOOGLE_API_KEY=your-key-here
GOOGLE_SEARCH_ENGINE_ID=your-cse-id
NEWSAPI_KEY=your-key-here

# Monitoring
USE_MOCK_APIS=true           # Start with mock, switch to false for real APIs
MIN_RELEVANCE_SCORE=0.5
SCAN_LOOKBACK_DAYS=7

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Settings UI

Configure application settings via the **⚙️ Settings** page in the UI:

- **General**: Application mode, database path
- **API Configuration**: Enable/disable APIs, configure keys
- **Monitoring**: Scan frequency, relevance thresholds
- **Notifications**: Email alerts, quiet hours
- **Display**: UI preferences, date formats

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Write tests** (maintain 80%+ coverage)
5. **Run tests** (`pytest`)
6. **Commit changes** (`git commit -m 'Add: amazing feature'`)
7. **Push to branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide
- Add type hints to new code
- Write docstrings for public functions
- Include tests for new features
- Update documentation as needed

See [Developer Guide](docs/DEVELOPER_GUIDE.md#contributing-guidelines) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

### Built With

- [Streamlit](https://streamlit.io/) - Beautiful web apps in Python
- [Plotly](https://plotly.com/) - Interactive charts
- [SQLite](https://www.sqlite.org/) - Embedded database
- [Pytest](https://pytest.org/) - Testing framework

### Inspired By

- Modern customer success platforms
- Intelligence gathering tools
- Portfolio monitoring solutions

### Special Thanks

- The Streamlit community for an amazing framework
- All contributors and testers
- Early adopters providing valuable feedback

---

## 📞 Support & Contact

- **Documentation**: Check the `docs/` folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@example.com
- **Community**: [Join our Discord/Slack](#)

---

## 🎓 Learn More

### Tutorials

- [Getting Started in 5 Minutes](docs/USER_GUIDE.md#quick-start)
- [Adding Your First Client](docs/USER_GUIDE.md#adding-your-first-client)
- [Setting Up Automation](docs/USER_GUIDE.md#setting-up-automation)
- [Creating Custom Reports](docs/USER_GUIDE.md#creating-reports)

### Advanced Topics

- [Architecture Deep Dive](docs/DEVELOPER_GUIDE.md#architecture-overview)
- [Adding New Collectors](docs/DEVELOPER_GUIDE.md#adding-a-new-collector)
- [Extending Event Types](docs/DEVELOPER_GUIDE.md#adding-a-new-event-type)
- [Performance Optimization](docs/DEPLOYMENT.md#performance-tuning)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐️ on GitHub!

---

<div align="center">

**Built with ❤️ for Customer Success Professionals**

[Documentation](docs/) · [Report Bug](https://github.com/your-repo/issues) · [Request Feature](https://github.com/your-repo/issues)

</div>
