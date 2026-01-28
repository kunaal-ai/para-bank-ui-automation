# Traceability Matrix

This document tracks the relationship between User Stories, Test Cases, and their implementation status in the ParaBank UI Automation project.

## Matrix

| ID | User Story | Test Case Name | Implementation Path | Status |
|----|------------|----------------|---------------------|--------|
| **US-01** | **User Authentication** | Login Successful | `tests/test_login.py`, `tests/test_home_login.py` | ✅ Passed |
| | | Login Invalid Credentials | `tests/test_login.py` | ✅ Passed |
| | | Successful Logout | `tests/test_logout.py` | ✅ Passed |
| | | Forget Login Flow | `tests/test_home_login.py` | ✅ Passed |
| | | Login with Empty Credentials | `tests/test_login.py` | ✅ Passed |
| | | Forgot Login Info Navigation | `tests/test_login.py` | ✅ Passed |
| | | Login After Logout | `tests/test_login.py` | ✅ Passed |
| **US-02** | **Account Management** | Open Checking Account | `tests/test_open_account.py` | ✅ Passed |
| | | Open Savings Account | `tests/test_open_account.py` | ✅ Passed |
| | | Open Account Type Options | `tests/test_open_account.py` | ✅ Passed |
| | | Account Overview Details | `tests/test_account_overview.py` | ✅ Passed |
| | | Navigate to Account Details | `tests/test_account_overview.py` | ✅ Passed |
| | | Account Activity Filtering | `tests/test_account_overview.py` | ✅ Passed |
| | | Total Balance Presence | `tests/test_account_overview.py` | ✅ Passed |
| **US-03** | **Fund Transfer** | Transfer Funds Success | `tests/test_transfer_funds.py` | ✅ Passed |
| | | Transfer Funds Empty Amount | `tests/test_transfer_funds.py` | ✅ Passed |
| | | Transfer Funds Navigation & Fields | `tests/test_transfer_funds.py` | ✅ Passed |
| **US-04** | **Bill Payment** | Submit Bill Pay Correct Values | `tests/test_bill_pay.py` | ✅ Passed |
| | | Bill Pay Validation Errors | `tests/test_bill_pay.py` | ✅ Passed |
| | | Bill Pay Mismatch Account | `tests/test_bill_pay.py` | ✅ Passed |
| | | Bill Pay Invalid Amount | `tests/test_bill_pay.py` | ✅ Passed |
| **US-05** | **Loan Request** | Request Loan Denied | `tests/test_request_loan.py` | ✅ Passed |
| | | Request Loan Navigation | `tests/test_request_loan.py` | ✅ Passed |
| | | Request Loan Empty Fields | `tests/test_request_loan.py` | ✅ Passed |
| | | Request Loan Form Elements | `tests/test_request_loan.py` | ✅ Passed |
| **US-06** | **Transaction History** | Find Transactions by Amount | `tests/test_find_transactions.py` | ✅ Passed |
| | | Find Transactions by Date | `tests/test_find_transactions.py` | ✅ Passed |
| | | Find Transactions Navigation | `tests/test_find_transactions.py` | ✅ Passed |
| | | Find Transactions by ID Invalid | `tests/test_find_transactions.py` | ✅ Passed |
| | | Find Transactions Empty Fields | `tests/test_find_transactions.py` | ✅ Passed |
| **US-07** | **Profile Management** | Update Zip Code Successful | `tests/test_update_contact_info.py` | ✅ Passed |
| | | Update Contact Info Validation | `tests/test_update_contact_info.py` | ✅ Passed |
| | | Update Full Profile | `tests/test_update_contact_info.py` | ✅ Passed |
| **US-08** | **Registration** | New User Registration | `tests/test_registration.py` | ✅ Passed |
| | | Registration Validation Errors | `tests/test_registration.py` | ✅ Passed |
| | | Registration Duplicate Username | `tests/test_registration.py` | ✅ Passed |
| | | Registration Password Mismatch | `tests/test_registration.py` | ✅ Passed |
| **US-09** | **Customer Care** | Contact Us Form Submission | `tests/test_contact_us.py` | ✅ Passed |
| | | Contact Us Validation | `tests/test_contact_us.py` | ✅ Passed |
| | | Contact Us Elements Visibility | `tests/test_contact_us.py` | ✅ Passed |
| **US-10** | **Site Navigation** | Footer About Us Navigation | `tests/test_site_navigation.py` | ✅ Passed |
| | | Footer Services Navigation | `tests/test_site_navigation.py` | ✅ Passed |
| | | Home Page Logo Navigation | `tests/test_site_navigation.py` | ✅ Passed |
| | | Header Home Link | `tests/test_site_navigation.py` | ✅ Passed |
| | | Header Contact Link | `tests/test_site_navigation.py` | ✅ Passed |
| | | Header About Link | `tests/test_site_navigation.py` | ✅ Passed |
