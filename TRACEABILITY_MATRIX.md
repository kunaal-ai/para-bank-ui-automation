# Traceability Matrix

This document tracks the relationship between User Stories, Test Cases, and their implementation status in the ParaBank UI Automation project.

## Status Legend

- `✅ Covered`: Automated test exists and is mapped to a user story.
- Runtime outcomes (`passed`, `failed`, `xfailed`) are environment-dependent
  and should be reported separately in execution summaries.

## Latest Execution Snapshot (AWS Demo Profile)

- Result: `63 passed, 14 xfailed`
- Purpose: Demonstrates strong coverage with explicit handling for known
  backend instability.

## Matrix

| ID | User Story | Test Case Name | Implementation Path | Coverage Status |
|----|------------|----------------|---------------------|--------|
| **US-01** | **User Authentication** | Login Successful | `tests/test_login.py`, `tests/test_home_login.py` | ✅ Covered |
| | | Login Invalid Credentials | `tests/test_login.py` | ✅ Covered |
| | | Successful Logout | `tests/test_logout.py` | ✅ Covered |
| | | Forget Login Flow | `tests/test_home_login.py` | ✅ Covered |
| | | Login with Empty Credentials | `tests/test_login.py` | ✅ Covered |
| | | Forgot Login Info Navigation | `tests/test_login.py` | ✅ Covered |
| | | Login After Logout | `tests/test_login.py` | ✅ Covered |
| **US-02** | **Account Management** | Open Checking Account | `tests/test_open_account.py` | ✅ Covered |
| | | Open Savings Account | `tests/test_open_account.py` | ✅ Covered |
| | | Open Account Type Options | `tests/test_open_account.py` | ✅ Covered |
| | | Account Overview Details | `tests/test_account_overview.py` | ✅ Covered |
| | | Navigate to Account Details | `tests/test_account_overview.py` | ✅ Covered |
| | | Account Activity Filtering | `tests/test_account_overview.py` | ✅ Covered |
| | | Total Balance Presence | `tests/test_account_overview.py` | ✅ Covered |
| **US-03** | **Fund Transfer** | Transfer Funds Success | `tests/test_transfer_funds.py` | ✅ Covered |
| | | Transfer Funds Empty Amount | `tests/test_transfer_funds.py` | ✅ Covered |
| | | Transfer Funds Navigation & Fields | `tests/test_transfer_funds.py` | ✅ Covered |
| **US-04** | **Bill Payment** | Submit Bill Pay Correct Values | `tests/test_bill_pay.py` | ✅ Covered |
| | | Bill Pay Validation Errors | `tests/test_bill_pay.py` | ✅ Covered |
| | | Bill Pay Mismatch Account | `tests/test_bill_pay.py` | ✅ Covered |
| | | Bill Pay Invalid Amount | `tests/test_bill_pay.py` | ✅ Covered |
| **US-05** | **Loan Request** | Request Loan Denied | `tests/test_request_loan.py` | ✅ Covered |
| | | Request Loan Navigation | `tests/test_request_loan.py` | ✅ Covered |
| | | Request Loan Empty Fields | `tests/test_request_loan.py` | ✅ Covered |
| | | Request Loan Form Elements | `tests/test_request_loan.py` | ✅ Covered |
| **US-06** | **Transaction History** | Find Transactions by Amount | `tests/test_find_transactions.py` | ✅ Covered |
| | | Find Transactions by Date | `tests/test_find_transactions.py` | ✅ Covered |
| | | Find Transactions Navigation | `tests/test_find_transactions.py` | ✅ Covered |
| | | Find Transactions by ID Invalid | `tests/test_find_transactions.py` | ✅ Covered |
| | | Find Transactions Empty Fields | `tests/test_find_transactions.py` | ✅ Covered |
| **US-07** | **Profile Management** | Update Zip Code Successful | `tests/test_update_contact_info.py` | ✅ Covered |
| | | Update Contact Info Validation | `tests/test_update_contact_info.py` | ✅ Covered |
| | | Update Full Profile | `tests/test_update_contact_info.py` | ✅ Covered |
| **US-08** | **Registration** | New User Registration | `tests/test_registration.py` | ✅ Covered |
| | | Registration Validation Errors | `tests/test_registration.py` | ✅ Covered |
| | | Registration Duplicate Username | `tests/test_registration.py` | ✅ Covered |
| | | Registration Password Mismatch | `tests/test_registration.py` | ✅ Covered |
| **US-09** | **Customer Care** | Contact Us Form Submission | `tests/test_contact_us.py` | ✅ Covered |
| | | Contact Us Validation | `tests/test_contact_us.py` | ✅ Covered |
| | | Contact Us Elements Visibility | `tests/test_contact_us.py` | ✅ Covered |
| **US-10** | **Site Navigation** | Footer About Us Navigation | `tests/test_site_navigation.py` | ✅ Covered |
| | | Footer Services Navigation | `tests/test_site_navigation.py` | ✅ Covered |
| | | Home Page Logo Navigation | `tests/test_site_navigation.py` | ✅ Covered |
| | | Header Home Link | `tests/test_site_navigation.py` | ✅ Covered |
| | | Header Contact Link | `tests/test_site_navigation.py` | ✅ Covered |
| | | Header About Link | `tests/test_site_navigation.py` | ✅ Covered |
