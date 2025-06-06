"""Home Page """
import os
import json
from typing import Dict, Optional
from playwright.sync_api import Page, expect, BrowserContext


class HomePage:
    """Page objects and methods Home Page only"""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_name_text = page.locator("input[name=\"username\"]")
        self.password_text = page.locator("input[name=\"password\"]")
        self.log_in_button = page.locator("input.button")
        self.forget_login_button = page.locator(
            "#loginPanel > p:nth-child(2) > a:nth-child(1)"
        )

    def load(self, base_url: Optional[str] = None):
        """Navigate to the home page.
        
        Args:
            base_url: The base URL to navigate to. If not provided, uses the BASE_URL environment variable.
        """
        if not base_url:
            base_url = os.environ.get('BASE_URL', 'https://parabank.parasoft.com/parabank/')
        self.page.goto(base_url)
    
    def save_storage_state(self, path: str = "state.json"):
        """Save the browser's storage state to a file.
        
        Args:
            path: Path to save the storage state to.
        """
        storage = self.page.context.storage_state(path=path)
        return storage
        
    def restore_storage_state(self, path: str = "state.json"):
        """Restore the browser's storage state from a file.
        
        Args:
            path: Path to load the storage state from.
        """
        if os.path.exists(path):
            self.page.context.clear_cookies()
            self.page.goto('about:blank')  # Ensure we're on a blank page
            with open(path, 'r') as f:
                storage_state = json.load(f)
            self.page.context.add_cookies(storage_state['cookies'])
            return True
        return False

    def user_log_in(self, username: str = None, password: str = None):
        """Log in with the provided credentials or from environment variables.
        
        Args:
            username: Username to log in with. If not provided, uses 'john'.
            password: Password to log in with. If not provided, uses PASSWORD environment variable.
        """
        if username is None:
            username = "john"
        if password is None:
            password = os.environ.get('PASSWORD', 'demo')
            
        self.user_name_text.fill(username)
        self.password_text.fill(password)
        self.log_in_button.click()
        
        # Verify login was successful
        expect(self.page).to_have_url(re.compile(r'.*/overview\.htm$'))

    def forget_login(self):
        self.forget_login_button.click()
