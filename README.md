# ParaBank UI Automation

Automated UI testing for ParaBank using Playwright, Python, and Jenkins CI/CD.

## Technologies

### Testing & Automation
- 🐍 **Python** - Core programming language
- 🎭 **Playwright** - Modern web testing framework
- 📊 **Pytest** - Test runner and framework
- 🏗️ **Page Object Model** - Design pattern for test maintenance

### CI/CD & Infrastructure
- 🔄 **Jenkins** - Continuous Integration/Deployment
- 🐳 **Docker** - Containerization
- 📦 **Docker Compose** - Multi-container orchestration

### Monitoring & Reporting
- 📈 **Prometheus** - Metrics collection
- 📊 **Grafana** - Metrics visualization
- 📝 **HTML Reports** - Test execution reports
- 📋 **JUnit XML** - CI integration reports

### Development Tools
- 🐙 **Git** - Version control
- 📦 **pip** - Package management
- 🔍 **pytest-xdist** - Parallel test execution
- 🎥 **Video Recording** - Failed test capture

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

## Key Features

- 🧪 Playwright-based UI testing
- 📊 HTML and JUnit XML reports
- 🔄 Jenkins CI/CD pipeline
- 📈 Prometheus metrics & Grafana dashboards
- 🎥 Video recording for failed tests
- 🔁 Automatic retry for flaky tests

## Project Structure

```
.
├── src/              # Source code
│   ├── pages/       # Page Object Models
│   └── utils/       # Utilities
├── tests/           # Test files
├── config/          # Configuration files
├── docker/          # Docker configurations
└── scripts/         # Helper scripts
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

## Contributing

1. Make your changes
2. Run tests locally: `./run-tests.sh`
3. Push changes to trigger CI/CD pipeline