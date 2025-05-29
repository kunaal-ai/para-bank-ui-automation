# para-bank-ui-automation
Banking domain: Python, Rspec, Playwright, CI/CD Jenkins, HTML reports, Prometheus, Grafana

# Run Test
- Headed Mode: ```pytest --headed``` 
- Selected Browser: ```pytest --browser webkit --browser firefox```
- Run specific tests file: ```pytest test_login.py```
- Run a Test case: ```pytest -k test_functiona_name```

# Parallel
```pytest --numprocesses 2```
- NOTE: make sure ```pytest-xdist``` is installed

# Debugging
- All tests: ```PWDEBUG=1 pytest -s```
- One Test file: ```PWDEBUG=1 pytest -s test_file.py```
- Single Test case: ```PWDEBUG=1 pytest -s -k test_function_name```

# Monitoring with Prometheus and Grafana

This project includes monitoring capabilities using Prometheus, Pushgateway, and Grafana to track test metrics.

## Prerequisites

- Docker and Docker Compose must be installed
- Check your Docker installation: `python monitoring.py check-docker`

## Setup and Usage

1. Start monitoring services:
   ```
   python monitoring.py start
   ```

2. Run your tests as usual. Metrics will be automatically collected and pushed to Prometheus via Pushgateway:
   ```
   pytest
   ```
   You'll see messages like `Metrics pushed successfully to Pushgateway` during test execution.

3. Access monitoring dashboards:
   - Prometheus: http://localhost:9090
   - Pushgateway: http://localhost:9091
   - Grafana: http://localhost:3000 (default credentials: admin/admin)

4. Stop monitoring services when done:
   ```
   python monitoring.py stop
   ```

5. Check monitoring services status:
   ```
   python monitoring.py status
   ```

## How It Works

The monitoring system uses three main components:

1. **Prometheus**: Collects and stores metrics data, provides querying capabilities
2. **Pushgateway**: Allows tests to push metrics that Prometheus can scrape
3. **Grafana**: Provides beautiful dashboards to visualize the metrics

During test execution, metrics are automatically pushed to the Pushgateway after each test. Prometheus scrapes these metrics from the Pushgateway and makes them available for querying and visualization in Grafana.

## Available Metrics

- `test_runs_total`: Total number of test runs
- `test_passes_total`: Total number of passed tests
- `test_failures_total`: Total number of failed tests
- `test_duration_seconds`: Test execution time in seconds (histogram)
