# SmartMapParis 3D

![Logo](static/images/logo.png)

Professional interactive web application for visualizing real estate prices in Paris and France with 3D mapping technology.

## Features

- **3D Real Estate Visualization**: Paris by arrondissements and districts, France by departments
- **Real-time Data**: Price per m² and transaction counts (2020-2024)
- **Multilingual Interface**: French / English support
- **AI Assistant**: Integrated chat with real estate predictions powered by Ollama
- **Visual Themes**: Satellite, street, dark mode
- **Price Predictions**: 2025 forecasting with linear trend analysis
- **Official Data Sources**: Paris quartiers, arrondissements, and French departments

## Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) (for AI assistant)

### Installation
```bash
# Clone the repository
git clone https://github.com/[your-username]/SmartMapParisV5.git
cd SmartMapParisV5

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Populate with data
python manage.py populate_quartiers
python manage.py import_all_france_departments
```

### Launch
```bash
# Activate environment
source .venv/bin/activate

# Start development server
python manage.py runserver

# Open http://localhost:8000
```

## Architecture

### Project Structure
```
SmartMapParisV5/
├── .gitignore                 # Professional git configuration
├── README.md                  # This documentation
├── requirements.txt           # Minimal dependencies (Django, Ollama, Requests)
├── manage.py                  # Django management
├── db.sqlite3                 # SQLite database
├── smartmap/                  # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # Optimized settings
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI configuration
├── prices/                    # Main application
│   ├── models.py              # Data models (Arrondissement, Quartier, etc.)
│   ├── views.py               # Main views
│   ├── api_views.py           # REST API endpoints
│   ├── ai_views.py            # AI assistant integration
│   ├── predictions.py         # Price prediction algorithms
│   ├── opendata_views.py      # OpenData API integration
│   ├── api_urls.py            # API URL routing
│   ├── apps.py                # App configuration
│   ├── migrations/            # Database migrations
│   └── management/commands/   # Data import commands
├── templates/
│   └── index.html             # Main application template
└── static/                    # Frontend assets
    ├── js/app.js              # Main JavaScript application
    ├── css/styles.css         # Styling
    └── images/logo.png        # Assets
```

### Technology Stack
- **Backend**: Django 4.2, Python 3.9
- **Frontend**: JavaScript ES6, Mapbox GL JS
- **AI**: Ollama + LLaMA 3.2
- **Database**: SQLite
- **APIs**: RESTful JSON endpoints

## API Documentation

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/years/` | GET | Available data years |
| `/api/prices/` | GET | Paris arrondissement prices |
| `/api/quartiers/` | GET | Paris districts GeoJSON |
| `/api/quartiers/prices/` | GET | District-level prices |
| `/api/france/prices/` | GET | France department prices |
| `/api/france/departements/` | GET | Departments GeoJSON |
| `/api/ai/chat/` | POST | AI assistant chat |
| `/api/ai/predictions/` | POST | 2025 price predictions |

### Example Usage
```bash
# Get available years
curl http://localhost:8000/api/years/

# Get Paris prices for 2024
curl http://localhost:8000/api/prices/?year=2024

# Chat with AI assistant
curl -X POST http://localhost:8000/api/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the trends in Paris real estate?", "language": "en"}'
```

## AI Assistant

The integrated AI assistant uses **Ollama** with the **LLaMA 3.2** model to provide:

### Capabilities
- **Market Analysis**: Real estate trend analysis
- **Natural Language**: Questions in French or English
- **Predictions**: 2025 price forecasting
- **Data Insights**: Statistical analysis of DVF data
- **Location Advice**: Investment recommendations

### Prediction Algorithm
- **Method**: Linear trend analysis based on 2020-2024 data
- **Scope**: Paris arrondissements and France departments
- **Accuracy**: Beginner-level forecasting (actual results may vary)

## Data Sources

### Official Sources
- **Paris Districts**: [opendata.paris.fr/quartier_paris](https://opendata.paris.fr/explore/dataset/quartier_paris/)
- **Paris Arrondissements**: [opendata.paris.fr/arrondissements](https://opendata.paris.fr/explore/dataset/arrondissements/)
- **French Departments**: [france-geojson.gregoiredavid.fr](https://france-geojson.gregoiredavid.fr/)

### Data Coverage
- **80 Paris Districts** with authentic names
- **20 Paris Arrondissements** with full statistics
- **101 French Departments** including overseas territories
- **5 Years** of price evolution (2020-2024)

## Features

### Interactive 3D Map
- **Enhanced Zoom**: Double-click, right-click, and left-click zoom
- **3D Visualization**: Height-based price representation
- **Color Mapping**: Gradient from low to high prices
- **Hover Information**: Detailed price and transaction data
- **Theme Support**: Multiple visual styles

### Multilingual Support
- **French Interface**: Default for French users
- **English Interface**: Complete translation available
- **Smart Detection**: Automatic language adaptation
- **Professional UX**: Seamless language switching

## Development

### Code Quality
- **Professional Comments**: 100% English documentation
- **Clean Architecture**: Modular and maintainable
- **Minimal Dependencies**: Only essential packages
- **Error Handling**: Robust exception management
- **Type Hints**: Python type annotations

### Performance Optimizations
- **Efficient Queries**: Optimized database operations
- **Minimal Static Files**: No duplicate assets
- **Clean Dependencies**: Removed unused packages (DRF)
- **Professional Structure**: Industry-standard organization

### Testing
```bash
# Run Django checks
python manage.py check

# Test API endpoints
curl http://localhost:8000/api/years/
```

## Deployment

### Quick Deploy with Script
```bash
# Run the automated deployment script
./deploy.sh
```

### Manual Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Setup database and data
python manage.py migrate
python manage.py populate_quartiers
python manage.py import_all_france_departments

# Collect static files
python manage.py collectstatic --noinput
```

### Production Platforms

#### Heroku
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
git push heroku main
```

#### Railway
```bash
# Connect your GitHub repo to Railway
# Set environment variables in Railway dashboard:
# DEBUG=False
# ALLOWED_HOSTS=your-domain.railway.app
```

#### Render
```bash
# Connect your GitHub repo to Render
# Use these build/start commands:
# Build: pip install -r requirements.txt
# Start: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn smartmap.wsgi
```

### Environment Variables
```bash
# Required for production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
MAPBOX_TOKEN=your_mapbox_token_here  # Optional, default provided
```

## Future Enhancements

### Planned Features
- **Advanced Predictions**: Machine learning models
- **More Data Sources**: Additional real estate APIs
- **User Authentication**: Save preferences and favorites
- **Advanced Analytics**: Deeper market insights
- **Mobile Optimization**: Responsive design improvements

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

MIT License - Feel free to use this project for educational or commercial purposes.

## Acknowledgments

- **OpenData Paris** for providing authentic district data
- **Mapbox** for excellent mapping technology
- **Ollama** for local AI capabilities
- **Django** for robust web framework

---

**SmartMapParis 3D** - Professional real estate visualization tool for the French market. 