# ParaBank UI Automation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Automated UI testing framework for ParaBank using Playwright, Python, and modern development practices.

## 🚀 Features

- **Cross-browser Testing**: Support for Chromium, Firefox, and WebKit
- **Parallel Execution**: Run tests in parallel with pytest-xdist
- **Rich Reporting**: Allure reports, JUnit XML, and HTML coverage reports
- **CI/CD Ready**: Pre-configured for GitHub Actions and Jenkins with Docker
- **Type Checking**: Full mypy integration for static type checking
- **Code Quality**: Pre-commit hooks with Black, isort, and flake8
- **Test Stability**: Automatic retries for flaky tests
- **Visual Testing**: Screenshot and video recording on failure
- **Centralized Logger**: Automatic logging to console and file with structured format

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

1. **Start Docker Desktop** (if using monitoring)
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
   # Basic test run (uses dev environment by default)
   pytest

   # Run tests against specific environment
   pytest --env=dev
   pytest --env=stage
   pytest --env=prod

   # Run tests in parallel (4 workers)
   pytest -n 4

   # Run specific test file
   pytest tests/test_login.py

   # Run specific test with browser UI (headed mode)
   pytest tests/test_login.py --headed

   # Run tests with specific browser
   pytest --browser=firefox
   pytest --browser=webkit

   # Run smoke tests only
   pytest -m smoke

   # Run with coverage report
   pytest --cov=src --cov-report=html

   # Run with Allure reporting
   pytest --alluredir=allure-results
   allure serve allure-results

   # Run with verbose output
   pytest -v

   # Run with detailed logging
   pytest --log-cli-level=DEBUG
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

### Environment-Based Configuration

The project supports multiple environments (dev, stage, prod) using JSON configuration files. Each environment has its own configuration file in the `config/` directory.

#### Setting Up Environment Configuration

1. **Copy the example configuration file for your environment:**
   ```bash
   # For development environment
   cp config/dev.json.example config/dev.json

   # For staging environment
   cp config/stage.json.example config/stage.json

   # For production environment
   cp config/prod.json.example config/prod.json
   ```

2. **Edit the configuration file with your environment-specific values:**
   ```json
   {
     "base_url": "https://parabank.parasoft.com/parabank",
     "api_url": "https://parabank.parasoft.com/parabank/api",
     "browser": "chromium",
     "headless": true,
     "timeout": 30000,
     "users": {
       "valid": {
         "username": "your_username",
         "password": "your_password"
       },
       "invalid": {
         "username": "invalid",
         "password": "invalid"
       }
     }
   }
   ```

#### Running Tests Against Different Environments

```bash
# Run tests against development environment (default)
pytest

# Run tests against staging environment
pytest --env=stage

# Run tests against production environment
pytest --env=prod
```

#### Configuration File Structure

Each environment configuration file (`config/{env}.json`) contains:

- **base_url**: Base URL of the ParaBank application
- **api_url**: API endpoint URL
- **browser**: Browser to use (`chromium`, `firefox`, or `webkit`)
- **headless**: Run browser in headless mode (`true`/`false`)
- **timeout**: Default timeout in milliseconds
- **users**: Test user credentials
  - **valid**: Valid user credentials for positive tests
  - **invalid**: Invalid credentials for negative tests

#### Accessing Configuration in Tests

```python
def test_example(env_config):
    """Test using environment configuration."""
    # Access configuration as attributes
    base_url = env_config.base_url
    browser = env_config.browser

    # Or access as dictionary
    timeout = env_config["timeout"]
    username = env_config.users["valid"]["username"]
```

### Environment Variables (Legacy)

For backward compatibility, you can still use `.env` file, but environment-based JSON configuration is recommended:

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

Pre-commit hooks are configured to automatically format and check your code before each commit. This ensures code quality and consistency across the project.

#### Installation

```bash
# Install pre-commit hooks (run once after cloning)
pre-commit install

# Install hooks for commit messages (optional)
pre-commit install --hook-type commit-msg
```

#### Running Pre-commit Hooks

```bash
# Run hooks on all files (useful for CI/CD or manual checks)
pre-commit run --all-files

# Run hooks only on staged files (automatic on commit)
pre-commit run

# Run a specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

#### Configured Hooks

The project includes the following pre-commit hooks (configured in `.pre-commit-config.yaml`):

1. **Basic Checks**
   - `trailing-whitespace`: Removes trailing whitespace
   - `end-of-file-fixer`: Ensures files end with a newline
   - `check-yaml`: Validates YAML files
   - `check-json`: Validates JSON files
   - `check-toml`: Validates TOML files
   - `check-added-large-files`: Prevents committing large files
   - `check-merge-conflict`: Detects merge conflict markers
   - `check-case-conflict`: Detects case conflicts in filenames

2. **Code Formatting**
   - `black`: Automatic code formatting (Python)
   - `isort`: Import sorting with black profile

3. **Code Quality**
   - `flake8`: Linting with bugbear plugin (max line length: 100)
   - `pylint`: Advanced linting with custom configuration
   - `mypy`: Static type checking (excludes tests directory)
   - `bandit`: Security linting (excludes tests and venv)
   - `pip-audit`: Dependency vulnerability scanning

#### Bypassing Pre-commit Hooks

If you need to bypass pre-commit hooks (not recommended):

```bash
# Skip hooks for a single commit
git commit --no-verify -m "Emergency fix"

# Note: This should only be used in exceptional circumstances
```

#### Troubleshooting Pre-commit

```bash
# Update pre-commit hooks to latest versions
pre-commit autoupdate

# Clear pre-commit cache if issues occur
pre-commit clean

# Run hooks with verbose output
pre-commit run --all-files --verbose
```

## 📊 Reporting

- **HTML Reports**: `pytest --html=reports/report.html`
- **Coverage Reports**: `pytest --cov=src --cov-report=html`
- **Allure Reports**:
  ```bash
  pytest --alluredir=allure-results
  allure serve allure-results
  ```
## 📝 Centralized Logging

The project includes a centralized logging system that automatically logs test execution to both console and file. The logger is configured in `conftest.py` and available throughout the test suite.

### Features

- **Automatic Setup**: Logger is automatically configured when tests run
- **Dual Output**: Logs to both console (stdout) and file (`logs/test_run.log`)
- **Structured Format**: Consistent log format with timestamps
- **Test Lifecycle Logging**: Automatically logs test start, completion, and failures

### Usage

```python
import logging

# Get the centralized logger
logger = logging.getLogger("parabank")

def test_example():
    logger.info("Starting test")
    try:
        # Test code
        logger.debug("Debug information")
        logger.info("Test step completed")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
    finally:
        logger.info("Test completed")
```

### Log Levels

- **DEBUG**: Detailed debugging information (function calls, variable values)
- **INFO**: General test progress and important events
- **WARNING**: Non-critical issues that don't fail tests
- **ERROR**: Test failures and exceptions
- **CRITICAL**: Critical errors that may stop test execution

### Configuration

The logger is automatically configured in `conftest.py` with the following settings:

- **Log File**: `logs/test_run.log` (created automatically)
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Date Format**: `%Y-%m-%d %H:%M:%S`
- **Level**: `DEBUG` (captures all log levels)
- **Handlers**:
  - Console handler (stdout)
  - File handler (logs/test_run.log)

### Custom Logger Setup

For custom logger configuration, use the utility function:

```python
from src.utils.logger import setup_logger
from pathlib import Path

# Create a custom logger
custom_logger = setup_logger(
    name="custom_module",
    log_level="INFO",
    log_file=Path("logs/custom.log")
)
```

### Test Session Logging

The framework automatically logs:
- Test session start/end
- Individual test start/completion
- Test failures with stack traces
- Session completion status

### Viewing Logs

```bash
# View log file in real-time
tail -f logs/test_run.log

# Search logs for errors
grep ERROR logs/test_run.log

# View last 100 lines
tail -n 100 logs/test_run.log
```


## 🐳 Docker & Monitoring

### Monitoring Stack Components
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Pushgateway**: Temporary metrics storage for batch jobs
- **Jenkins**: CI/CD pipeline

### Management Commands

```bash
# Start monitoring services
python -m src.utils.monitoring start

# Stop monitoring services
python -m src.utils.monitoring stop

# Check status of services
python -m src.utils.monitoring status

# Check if Docker is installed
python -m src.utils.monitoring check-docker
```

### Accessing Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jenkins**: http://localhost:8080

## 📊 Test Metrics & Monitoring

The project includes comprehensive test metrics collection and monitoring capabilities.

### Metrics Collection

Test metrics are automatically collected during test execution and pushed to Prometheus via Pushgateway:

- **Test Runs**: Total number of test executions
- **Test Passes**: Number of passed tests
- **Test Failures**: Number of failed tests
- **Test Duration**: Execution time for each test
- **Memory Usage**: Memory consumption during test execution
- **Performance Score**: Calculated performance metric (0-100)

### Using TestMetrics Context Manager

```python
from src.utils.metrics_pusher import TestMetrics

def test_example():
    with TestMetrics(test_name="test_example"):
        # Your test code here
        pass
    # Metrics are automatically pushed when context exits
```

### Manual Metrics Push

```python
from src.utils.metrics_pusher import push_metrics

# Push metrics manually
push_metrics(job_name="custom-job-name")
```

### Metrics Configuration

Metrics are configured in `src/utils/metrics_pusher.py`:
- **Pushgateway URL**: `localhost:9091` (default)
- **Job Name**: `para-bank-tests` (default)
- **Registry**: Prometheus CollectorRegistry

### Viewing Metrics

1. **Prometheus UI**: http://localhost:9090
   - Query: `test_runs_total`
   - Query: `test_passes_total`
   - Query: `test_failures_total`
   - Query: `test_duration_seconds`

2. **Grafana Dashboards**: http://localhost:3000
   - Pre-configured dashboards in `config/grafana/provisioning/dashboards/`
   - Custom queries and visualizations

## 🔒 Security

The project includes multiple security scanning tools configured in both pre-commit hooks and CI/CD pipelines:

### Security Tools

1. **Bandit** - Security linter for Python code
   - Scans for common security issues
   - Configured in `.bandit.yaml`
   - Runs in pre-commit hooks and Jenkins pipeline
   - Excludes test files and virtual environments

2. **pip-audit** - Dependency vulnerability scanner
   - Scans `requirements.txt` for known vulnerabilities
   - Checks against Python vulnerability databases
   - Runs in pre-commit hooks and Jenkins pipeline

### Running Security Checks

```bash
# Run bandit security scan
bandit -r src/ -f json -o bandit-report.json

# Run pip-audit
pip-audit --requirement requirements.txt

# Or use pre-commit
pre-commit run bandit --all-files
pre-commit run pip-audit --all-files
```

## 🧹 Cleanup & Maintenance

### Cleanup Script

The project includes a Python cleanup script to remove temporary files:

```bash
# Run cleanup script
python scripts/cleanup.py

# Or use the shell script
./scripts/cleanup.sh
```

The cleanup script removes:
- Python cache files (`__pycache__`, `*.pyc`)
- Pytest cache (`.pytest_cache`)
- Coverage files (`.coverage`, `coverage.xml`, `htmlcov/`)
- Build artifacts (`build/`, `dist/`, `*.egg-info/`)
- Virtual environments (`venv/`, `.venv`)
- IDE files (`.mypy_cache/`, `.tox/`)

### Manual Cleanup

```bash
# Remove all Python cache files
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove pytest cache
rm -rf .pytest_cache

# Remove coverage files
rm -rf .coverage coverage.xml htmlcov/
```
