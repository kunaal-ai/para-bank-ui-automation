# para-bank-ui-automation
Banking domain: Python, Rspec,  Playwright, CI/CD Jenkins, HTML reports

# Run Test
- Headed Mode: ```pytest --headed``` 
- Selected Browser: ```pytest --browser webkit --browser firefox```
- Run specefic tests file: ```pytest test_login.py```
- Run a Test case: ```pytest -k test_functiona_name

# Parallel
```pytest --numprocesses 2```
- NOTE: make sure ```pytest-xdist``` is installed

# Debuging
- All tests: ```PWDEBUG=1 pytest -s```
- One Test file: ```PWDEBUG=1 pytest -s test_file.py```
- Single Test case: ```PWDEBUG=1 pytest -s -k test_function_name```
