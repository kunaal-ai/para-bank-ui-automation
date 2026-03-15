# Release Notes – AWS Deployment Enhancements

This document tracks all changes made to support the AWS deployment plan (Milestones 1–3). Each change is documented in **STAR format** (Situation, Task, Action, Result) to clearly show context and impact.

---

## Overview

| Change ID | Component | Milestone | Status |
|-----------|-----------|-----------|--------|
| RN-001 | docker-compose.aws.yml | M1 | Implemented |
| RN-002 | Prometheus config (parabank-app) | M2 | Implemented |
| RN-003 | Grafana datasource DS_PROMETHEUS | M2 | Implemented |
| RN-004 | Base URL env priority | M3 | Implemented |
| RN-005 | Circuit Breaker (500/429) | M3 | Implemented |
| RN-006 | Observability hook (TEST_RESULT) | M3 | Implemented |

---

## RN-001: docker-compose.aws.yml for EC2 Deployment

**Situation:**
The existing `docker-compose.yml` is built for local CI (test runner, Jenkins, pushgateway, Grafana, Prometheus). There is no standalone compose file for deploying only ParaBank, Prometheus, and Grafana on an AWS EC2 instance, which is needed for the portfolio AWS deployment.

**Task:**
Provide a ready-to-use Docker Compose file that can be copied to an EC2 instance and run with `docker compose up -d`, without requiring users to generate it via an AI prompt.

**Action:**
- Added `docker-compose.aws.yml` at repository root (or `docker/docker-compose.aws.yml`).
- Configured services: `parabank`, `prometheus`, `grafana` on network `test-backbone`.
- Applied resource limits (512mb/128mb/256mb) and healthchecks per AWS_deployment_plan.txt.
- Documented usage in `AWS_deployment_plan.txt` and README.

**Result:**
- Users can deploy the ParaBank stack on EC2 with a single `docker compose -f docker-compose.aws.yml up -d`.
- No new AWS resources beyond one t3.micro; stays within Free Tier.
- Enables Milestone 2 (config mounts) and Milestone 3 (test runner targeting EC2).

---

## RN-002: Prometheus Config for parabank-app Scrape

**Situation:**
The current `config/prometheus/prometheus.yml` is tuned for local CI (pushgateway, para-bank-tests, prometheus self-scrape). The AWS stack runs ParaBank as a separate container and needs a scrape job targeting `http://parabank:8080`.

**Task:**
Add (or extend) Prometheus configuration so the AWS stack can scrape the ParaBank container for metrics.

**Action:**
- Added scrape job `parabank-app` with target `http://parabank:8080`, scrape_interval 5s.
- Metrics path set to `/parabank/metrics` or `/metrics` (ParaBank may not expose Prometheus natively; config is prepared for when metrics are available).
- Retained default prometheus self-scrape job.
- Documented in `config/prometheus/README.md` or inline comments if ParaBank does not expose metrics.

**Result:**
- Prometheus in the AWS stack can scrape ParaBank when metrics are exposed.
- If ParaBank lacks metrics, the target may show "down"; pipeline is correctly configured for future exporters.
- Aligns with Milestone 2 telemetry setup.

---

## RN-003: Grafana Datasource DS_PROMETHEUS

**Situation:**
Grafana provisioning uses a datasource named "Prometheus". Some dashboards or scripts expect a datasource named `DS_PROMETHEUS`. The AWS stack should have a consistent, provisioned datasource for Prometheus.

**Task:**
Ensure Grafana automatically provisions a Prometheus datasource named `DS_PROMETHEUS` pointing to `http://prometheus:9090`.

**Action:**
- Updated `config/grafana/provisioning/datasources/prometheus.yml` (or added `datasources-aws.yml`) with name `DS_PROMETHEUS`, type prometheus, url `http://prometheus:9090`, isDefault true.
- Ensured the file is mounted in the Grafana container via docker-compose.aws.yml volumes.

**Result:**
- Grafana in the AWS stack connects to Prometheus without manual setup.
- Dashboards and scripts can reference `DS_PROMETHEUS`.
- Supports Milestone 2 automation goal.

---

## RN-004: Base URL Environment Variable Priority

**Situation:**
The `Config` class loads `base_url` from environment-specific JSON files (dev.json, stage.json, prod.json). There is no support for overriding via the `BASE_URL` environment variable, which is required for running tests against an AWS EC2 instance without changing config files.

**Task:**
Allow `BASE_URL` (and optionally `EXECUTION_ENV=aws` + `AWS_BASE_URL`) to override the config file so users can run tests against EC2 with `export BASE_URL=http://<EC2_IP>:8080/parabank/`.

**Action:**
- Updated `config/__init__.py` so `Config` checks `os.environ.get("BASE_URL")` first when resolving base_url.
- Fallback order: BASE_URL env > EXECUTION_ENV=aws + AWS_BASE_URL > config file > default.
- Ensured trailing slash handling is consistent (e.g., always `/parabank/`).
- Documented in README and .env.example.

**Result:**
- Users can run `BASE_URL=http://1.2.3.4:8080/parabank/ pytest tests/` to target AWS.
- No config file changes needed for local vs AWS.
- Enables Milestone 3 framework integration.

---

## RN-005: Circuit Breaker for 500/429 Responses

**Situation:**
ParaBank running on a resource-constrained t3.micro can return 500 (Internal Server Error) or 429 (Too Many Requests) under load. Running the full test suite against such an unhealthy environment wastes time and produces noisy failures.

**Task:**
Implement a circuit breaker that tracks consecutive 500/429 responses. After 3 consecutive failures, abort the run immediately by raising a custom exception, so the suite stops gracefully instead of continuing to fail.

**Action:**
- Added `CircuitBreaker` class and `EnvironmentBlockedException` in `src/utils/stability.py`.
- Module-level counter for consecutive 500/429; reset on 2xx.
- Integrated Playwright `page.on("response", ...)` listener in conftest or page fixture to capture HTTP status.
- Raised `EnvironmentBlockedException` when counter reaches 3; pytest exits with clear error message.
- Documented in conftest.py and stability module.

**Result:**
- Test run aborts after 3 consecutive 500/429 responses.
- Reduces wasted executions and clearer signal when ParaBank is unhealthy.
- Aligns with Milestone 3 resilience goal.

---

## RN-006: Observability Hook (TEST_RESULT)

**Situation:**
Test results are reported by pytest and, if configured, Healix/Pushgateway. There is no structured, per-test log output in a format suitable for external log parsing (e.g., for Prometheus, Datadog, or CI dashboards).

**Task:**
Add a pytest hook that prints one JSON line per test in the format `TEST_RESULT: {"name": "test_id", "status": "passed|failed|skipped", "latency_ms": 123}` for easy log aggregation and metrics pipelines.

**Action:**
- Implemented `pytest_runtest_makereport` hook in `conftest.py`.
- On test completion, print `TEST_RESULT: <json>` to stdout.
- Used `item.nodeid` as name, `report.outcome` as status, and `report.duration` (in ms) as latency_ms.
- Optional: gate via `EXECUTION_ENV=aws` or `TEST_RESULT_LOGGING=1` to reduce local log noise.

**Result:**
- Every test produces a machine-readable log line for observability pipelines.
- Enables Prometheus-friendly metrics and dashboards.
- Supports Milestone 3 observability goal.

---

## Changelog Summary

| Date | Change IDs | Description |
|------|------------|-------------|
| 2026-02-14 | RN-001 | Added docker-compose.aws.yml |
| 2026-02-14 | RN-002 | Added parabank-app scrape to Prometheus |
| 2026-02-14 | RN-003 | Added DS_PROMETHEUS Grafana datasource |
| 2026-02-14 | RN-004 | Base URL env priority in Config |
| 2026-02-14 | RN-005 | Circuit Breaker for 500/429 |
| 2026-02-14 | RN-006 | TEST_RESULT observability hook |
