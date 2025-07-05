# ParaBank UI Automation

Automated UI testing for ParaBank using Playwright, Python, and Jenkins CI/CD.

## Technologies

### Testing & Automation
- Python, Playwright, Pytest

### CI/CD & Infrastructure
- Jenkins, Docker, Docker Compose

### Monitoring & Reporting
- Prometheus - Metrics collection
- Grafana - Metrics visualization
- HTML Reports - Test execution reports
- JUnit XML - CI integration reports

### Development Tools
- pip - Package management
- pytest-xdist - Parallel test execution
- Video Recording - Failed test capture

## Quick Start

1. **Setup**
   ```bash
   git clone https://github.com/kunaal-ai/para-bank-ui-automation.git
   cd para-bank-ui-automation
   pip install -r requirements.txt
   playwright install
   ```

2. **Run Tests**
   ```bash
   # Run all tests
   pytest

   # Run with browser UI
   pytest --headed

   # Run specific test
   pytest tests/test_login.py
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Application URL | https://parabank.parasoft.com/parabank/ |
| `PASSWORD` | Test password | - |

## Monitoring

Start monitoring services:
```bash
python monitoring.py start
```

Access dashboards:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

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


