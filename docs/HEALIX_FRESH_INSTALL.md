# Fresh install Healix from TestPyPI

Use these steps to simulate a first-time user installing Healix from TestPyPI (no local healix repo).

## 1. Uninstall any existing Healix

```bash
cd /path/to/para-bank-ui-automation
# Use the same env you run tests with (e.g. my_env or .venv)
pip uninstall -y healix-ai
```

## 2. (Optional) Clear pip cache

```bash
pip cache purge
```

## 3. Install from TestPyPI

Dependencies (playwright, etc.) must come from PyPI; use `--extra-index-url`:

```bash
pip install --no-cache-dir -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple healix-ai==0.1.28
```

## 4. Confirm install

```bash
pip show healix-ai
# Location should be under your env's site-packages, not a path to the healix repo
```

## 5. Run a test that uses Healix

```bash
pytest tests/test_site_navigation.py::test_footer_about_us_navigation -s -n 0
```

You should see the Healix welcome banner at session start and healing behavior if the test triggers it.
