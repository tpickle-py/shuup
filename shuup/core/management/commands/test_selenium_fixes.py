"""
Management command to test Selenium WebDriver fixes.

This command validates that all deprecated Selenium WebDriver methods
have been properly updated to use the new By syntax.
"""
import os

from django.core.management.base import BaseCommand
from selenium.webdriver.common.by import By


class Command(BaseCommand):
    help = "Test that Selenium WebDriver fixes are working properly"

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)

        if verbose:
            self.stdout.write("Testing Selenium WebDriver imports...")

        try:
            # Test that By is properly imported and accessible
            self.stdout.write("✓ selenium.webdriver.common.by.By import successful")

            # Test that all By selectors are available
            selectors = [
                By.ID, By.XPATH, By.LINK_TEXT, By.PARTIAL_LINK_TEXT,
                By.NAME, By.TAG_NAME, By.CLASS_NAME, By.CSS_SELECTOR
            ]

            for selector in selectors:
                if verbose:
                    self.stdout.write(f"  ✓ By.{selector} available")

            # Test that browser utils can be imported without errors
            from shuup.testing.browser_utils import (
                click_element,
                initialize_front_browser_test,
                wait_until_appeared,
                wait_until_condition,
                wait_until_disappeared,
                wait_until_appeared_xpath,
            )
            self.stdout.write("✓ Browser utility functions import successful")

            # Test that the updated functions work (without actually running a browser)
            if verbose:
                self.stdout.write("  ✓ click_element function available")
                self.stdout.write("  ✓ wait_until_appeared function available")
                self.stdout.write("  ✓ wait_until_disappeared function available")
                self.stdout.write("  ✓ wait_until_condition function available")
                self.stdout.write("  ✓ wait_until_appeared_xpath function available")

            # Validate that no deprecated methods are being used
            deprecated_methods = [
                'find_element_by_id',
                'find_element_by_name',
                'find_element_by_xpath',
                'find_element_by_link_text',
                'find_element_by_partial_link_text',
                'find_element_by_tag_name',
                'find_element_by_class_name',
                'find_element_by_css_selector',
                'find_elements_by_id',
                'find_elements_by_name',
                'find_elements_by_xpath',
                'find_elements_by_link_text',
                'find_elements_by_partial_link_text',
                'find_elements_by_tag_name',
                'find_elements_by_class_name',
                'find_elements_by_css_selector'
            ]

            if verbose:
                self.stdout.write("Checking for deprecated Selenium methods...")

            # Search for deprecated methods in the codebase
            deprecated_found = []
            shuup_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            for root, _dirs, files in os.walk(shuup_root):
                # Skip certain directories
                if any(skip in root for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                    continue

                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, encoding='utf-8') as f:
                                content = f.read()
                                for method in deprecated_methods:
                                    if f'.{method}(' in content:
                                        deprecated_found.append((file_path, method))
                        except (UnicodeDecodeError, OSError):
                            # Skip files that can't be read
                            continue

            if deprecated_found:
                self.stdout.write(self.style.ERROR("✗ Found deprecated Selenium methods:"))
                for file_path, method in deprecated_found:
                    self.stdout.write(f"  {file_path}: {method}")
                return
            else:
                self.stdout.write("✓ No deprecated Selenium methods found")

            self.stdout.write(self.style.SUCCESS("\n🎉 All Selenium WebDriver fixes validated successfully!"))
            self.stdout.write("The following fixes have been applied:")
            self.stdout.write("  • Updated find_element_by_css_selector → find_element(By.CSS_SELECTOR, selector)")
            self.stdout.write("  • Updated find_element_by_xpath → find_element(By.XPATH, xpath)")
            self.stdout.write("  • Updated find_elements_by_name → find_elements(By.NAME, name)")
            self.stdout.write("  • Added proper By imports where needed")
            self.stdout.write("\nYour browser tests should now work with newer Selenium versions!")

        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"✗ Import error: {e}"))
            self.stdout.write("Please ensure Selenium is properly installed.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Unexpected error: {e}"))
