# ParaBank UI Automation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Automated UI testing framework for ParaBank using Playwright, Python, and modern development practices.

## 🚀 Features

- **Cross-browser Testing**: Support for Chromium, Firefox, and WebKit
- **Parallel Execution**: Run tests in parallel with pytest-xdist
- **Rich Reporting**: Allure reports, JUnit XML, and HTML coverage reports
- **CI/CD Ready**: Pre-configured for GitHub Actions and Jenkins
- **Type Checking**: Full mypy integration for static type checking
- **Code Quality**: Pre-commit hooks with Black, isort, and flake8
- **Test Stability**: Automatic retries for flaky tests
- **Visual Testing**: Screenshot and video recording on failure

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kunaal-ai/para-bank-ui-automation.git
   cd para-bank-ui-automation
   ```

2. **Set up Python environment**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Install Playwright browsers
   playwright install
   ```

## 🚀 Running Tests

### Quick Start (Complete Workflow)

1. **Start Docker Desktop**
   - **macOS**:
     ```bash
     # Start Docker Desktop (if not running)
     open -a Docker
     
     # Verify Docker is running
     docker info
     ```
   - **Windows (PowerShell)**:
     ```powershell
     # Start Docker Desktop
     & 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
     
     # Verify Docker is running
     docker info
     ```
   - **Linux (systemd)**:
     ```bash
     # Start Docker service
     sudo systemctl start docker
     
     # Enable on boot (optional)
     sudo systemctl enable docker
     
     # Verify Docker is running
     docker info
     ```

2. **Start Monitoring Stack (Optional but recommended for test insights)**
   
   **Option 1: Using the helper script (recommended)**
   ```bash
   # Start all monitoring services (Prometheus, Grafana, etc.)
   python -m src.utils.monitoring start
   ```
   
   **Option 2: Manual Docker Compose**
   ```bash
   # Navigate to project root and run:
   docker compose up -d
   ```
   
   - Access dashboards:
     - Grafana: http://localhost:3000 (admin/admin)
     - Prometheus: http://localhost:9090
     
   > 💡 The helper script (`monitoring.py`) internally uses `docker compose up -d` but adds additional checks and status reporting.

3. **Run Tests**
   ```bash
   # Basic test run
   pytest
   
   # Run tests in parallel (4 workers)
   pytest -n 4
   
   # Run specific test with browser UI
   pytest tests/test_login.py --headed

# Run specific test with browser UI
pytest tests/test_login.py --headed

# Run smoke tests only
pytest -m smoke

# Run with coverage report
pytest --cov=src --cov-report=html

# Run with Allure reporting
pytest --alluredir=allure-results
allure serve allure-results
```

## 🏗️ Project Structure

```
parabank-ui-automation/
├── .github/               # GitHub Actions workflows
├── config/                # Configuration files
├── docs/                  # Documentation
├── reports/               # Test reports and screenshots
├── scripts/               # Development and utility scripts
│   ├── cleanup.sh         # Clean up test artifacts
│   ├── format.sh          # Code formatting script
│   ├── lint.sh            # Linting and code quality
│   └── typecheck.sh       # Static type checking
├── src/                   # Source code
│   ├── pages/             # Page Object Models
│   ├── utils/             # Helper functions
│   └── conftest.py        # Pytest fixtures
├── tests/                 # Test cases
│   ├── test_login.py      # Login tests
│   └── test_bill_pay.py   # Bill payment tests
├── .env.example          # Example environment variables
├── .pre-commit-config.yaml# Pre-commit hooks
└── pyproject.toml        # Project configuration
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory (use `.env.example` as a template):

```env
# Application
BASE_URL=https://parabank.parasoft.com/parabank/

# Authentication
USERNAME=testuser
PASSWORD=testpass

# Browser Configuration
BROWSER=chromium  # chromium, firefox, or webkit
HEADLESS=true
SLOW_MO=0  # milliseconds

# Test Execution
TIMEOUT=30000  # milliseconds
PARALLEL_WORKERS=4
RETRIES=2
```

## 🛠️ Development

### Development Scripts

All development scripts are located in the `scripts/` directory. Make them executable with `chmod +x scripts/*.sh` if needed.

```bash
# Format code (Black + isort)
./scripts/format.sh

# Run all linters
./scripts/lint.sh

# Run type checking
./scripts/typecheck.sh

# Clean up test artifacts
./scripts/cleanup.sh
```

### Manual Commands

```bash
# Format code with Black and isort
black .
isort .

# Run linter
pylint src/

# Run type checking
mypy src/
```

### Pre-commit Hooks

Pre-commit hooks are configured to automatically format and check your code:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📊 Reporting

- **HTML Reports**: `pytest --html=reports/report.html`
- **Coverage Reports**: `pytest --cov=src --cov-report=html`
- **Allure Reports**: 
  ```bash
  pytest --alluredir=allure-results
  allure serve allure-results
  ```




## 🐳 Docker & Monitoring

### Monitoring Stack Components
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Pushgateway**: Temporary metrics storage
- **Jenkins**: CI/CD pipeline

### Management Commands

```bash
# Start monitoring services
python -m src.utils.monitoring start

# Stop monitoring services
python -m src.utils.monitoring stop

# Check status of services
python -m src.utils.monitoring status
```

### Accessing Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jenkins**: http://localhost:8080

## Security
- bandit - security linter, configured in jenkins pipeline
- pip-audit - dependency (requirement.txt) security scanner, configured in jenkins pipeline


## TODO: Improvement Plan

#### 1. Set Up Pre-commit Hooks
- Add `.pre-commit-config.yaml` to run checks before commit
- Configure pre-commit to run Black, isort, pylint, and mypy
- Add pre-commit installation instructions to README

#### 2. Configure Linting Tools
- Create `.pylintrc` with project-specific rules
- Add `mypy.ini` for type checking configuration
- Configure Black and isort in `pyproject.toml` (partially done)

#### 3. CI/CD Integration
- Add linting stage to Jenkins pipeline
- Configure build to fail on linting errors
- Add automated code formatting check

#### 4. Automation Scripts
- Add `format.sh` for code formatting
- Add `lint.sh` for local linting
- Add `typecheck.sh` for type checking


