# AWS Deployment Implementation Action Plan

This document provides a detailed, step-by-step implementation plan for the enhancements defined in `AWS_deployment_plan.txt`. Each task maps to a specific milestone and includes acceptance criteria.

---

## Overview

| Milestone | Scope | Deliverables |
|-----------|-------|--------------|
| **M1** | Docker stack for EC2 | `docker-compose.aws.yml` |
| **M2** | Telemetry config | Prometheus scrape, Grafana datasource |
| **M3** | Framework integration | Base URL, Circuit Breaker, Observability |

---

## Milestone 1: Core Infrastructure & Networking

### Task 1.1: Create AWS docker-compose file

**Description:** Add a standalone `docker-compose.aws.yml` for deploying the ParaBank stack on EC2 (parabank, prometheus, grafana). This file is separate from the existing `docker-compose.yml` (which includes test runner, Jenkins, pushgateway for local CI).

**Files:**
- Create: `docker/docker-compose.aws.yml` (or `docker-compose.aws.yml` at repo root)

**Acceptance criteria:**
- [x] Version 3.8
- [x] Network `test-backbone` (bridge)
- [x] Service `parabank`: image parasoft/parabank:latest, port 8080, healthcheck, memory 512mb, restart unless-stopped
- [x] Service `prometheus`: image prom/prometheus, port 9090, memory 128mb, depends_on parabank, restart unless-stopped
- [x] Service `grafana`: image grafana/grafana, port 3000, memory 256mb, depends_on prometheus, restart unless-stopped
- [x] All services on `test-backbone` network

**Dependencies:** None

---

## Milestone 2: Telemetry & Monitoring Setup

### Task 2.1: Prometheus config for AWS stack

**Description:** Add a Prometheus config variant that scrapes `parabank-app` at `http://parabank:8080`. Keep existing `config/prometheus/prometheus.yml` for local CI; add AWS-specific variant or extend existing config.

**Files:**
- `config/prometheus/prometheus.yml` – add `parabank-app` scrape job if not present, or
- `config/prometheus/prometheus.aws.yml` – dedicated config for AWS stack

**Acceptance criteria:**
- [x] Scrape job `parabank-app` targeting `http://parabank:8080` with scrape_interval 5s
- [x] Default prometheus self-scrape (localhost:9090) retained
- [x] Metrics path `/parabank/metrics` (comment added; ParaBank may not expose metrics natively)

**Dependencies:** Task 1.1

### Task 2.2: Grafana datasource DS_PROMETHEUS

**Description:** Ensure Grafana provisioning includes a datasource named `DS_PROMETHEUS` pointing to `http://prometheus:9090`.

**Files:**
- `config/grafana/provisioning/datasources/prometheus.yml` (or new `datasources.aws.yml` if environment-specific)

**Acceptance criteria:**
- [x] Datasource name: `DS_PROMETHEUS`
- [x] Type: prometheus, URL: http://prometheus:9090
- [x] isDefault: true (Prometheus remains default; DS_PROMETHEUS for dashboard refs)

**Dependencies:** Task 1.1

### Task 2.3: Wire volumes into docker-compose.aws.yml

**Description:** Add volume mounts for Prometheus and Grafana in `docker-compose.aws.yml` so config files are loaded.

**Files:**
- `docker-compose.aws.yml` (or equivalent)

**Acceptance criteria:**
- [x] Prometheus: mount `./config/prometheus/prometheus.yml` to `/etc/prometheus/prometheus.yml`
- [x] Grafana: mount `./config/grafana/provisioning` to `/etc/grafana/provisioning`

**Dependencies:** Tasks 2.1, 2.2, 1.1

---

## Milestone 3: Automation Framework Integration

### Task 3.1: Base URL environment priority

**Description:** Update Config (or base_url resolution) so that `BASE_URL` from the environment overrides the config file. Priority: env `BASE_URL` > env `EXECUTION_ENV=aws` + `AWS_BASE_URL`/`PARABANK_URL` > config base_url > default.

**Files:**
- `config/__init__.py` – extend Config to check `os.environ.get("BASE_URL")` before `config["base_url"]`
- `config/dev.json.example` – document BASE_URL env var in comments or README

**Acceptance criteria:**
- [x] Setting `BASE_URL=http://1.2.3.4:8080/parabank/` overrides config
- [x] Trailing slash handling consistent (app expects /parabank/)
- [x] Default remains https://parabank.parasoft.com/parabank when no env set

**Dependencies:** None

### Task 3.2: Circuit Breaker for 500/429

**Description:** Implement a circuit breaker that tracks consecutive 500 and 429 HTTP responses. After 3 consecutive failures, raise `EnvironmentBlockedException` to abort the run. Reset counter on 2xx. Integrate via Playwright response listener in conftest or page fixture.

**Files:**
- `src/utils/stability.py` – add `CircuitBreaker` class, `EnvironmentBlockedException`, response tracking
- `conftest.py` – attach response listener to page/context to capture status codes and call circuit breaker

**Acceptance criteria:**
- [x] Counter increments on 500 or 429
- [x] Counter resets on 2xx
- [x] After 3 consecutive 500/429, raise exception and stop run
- [x] Integration in pytest lifecycle (page fixture + response listener)

**Dependencies:** None

### Task 3.3: Observability hook (TEST_RESULT)

**Description:** Add a pytest hook that prints `TEST_RESULT: {"name": "...", "status": "passed|failed|skipped", "latency_ms": N}` for each test. Use `pytest_runtest_makereport` and measure duration from the report.

**Files:**
- `conftest.py` – add `pytest_runtest_makereport` hook

**Acceptance criteria:**
- [x] One JSON line per test
- [x] Fields: name, status, latency_ms
- [x] Output to stdout for log aggregation / Prometheus parsing
- [x] Gated by `EXECUTION_ENV=aws` or `TEST_RESULT_LOGGING=1` to reduce local log noise

**Dependencies:** None

---

## Implementation Order

1. **Task 3.1** – Base URL (low risk, enables AWS runs)
2. **Task 3.3** – Observability (independent)
3. **Task 3.2** – Circuit Breaker (depends on page/context setup)
4. **Task 1.1** – docker-compose.aws.yml
5. **Task 2.1** – Prometheus config
6. **Task 2.2** – Grafana datasource
7. **Task 2.3** – Volume mounts in docker-compose.aws.yml

---

## Verification

After implementation:

1. **Local:** Run `pytest tests/` with default config – all tests pass.
2. **AWS:** Deploy `docker-compose.aws.yml` on EC2, set `BASE_URL=http://<EC2_IP>:8080/parabank/`, run `pytest` – tests target AWS.
3. **Circuit Breaker:** Simulate 500s (e.g., stop ParaBank) – suite aborts after 3.
4. **Observability:** Confirm `TEST_RESULT` lines in output.
