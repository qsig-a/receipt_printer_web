import unittest
from unittest.mock import MagicMock, patch, ANY
import os
import sys

# Mock dependencies
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['signalwire'] = MagicMock()
sys.modules['signalwire.rest'] = MagicMock()

from app import app, db

class TestUXEnhancement(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Reset mocks
        db.collection.return_value.document.return_value.get.return_value.exists = False

    @patch('app.CHARACTER_LIMIT', 50)
    def test_character_limit_ui_present(self):
        """
        Verify that character limit UI elements are rendered when CHARACTER_LIMIT is set.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        # Check for maxlength attribute
        self.assertIn('maxlength="50"', content)

        # Check for counter display
        self.assertIn('0/50', content)

        # Check for JS to update counter
        self.assertIn("document.getElementById('char-count').innerText", content)

    @patch('app.CHARACTER_LIMIT', None)
    def test_character_limit_ui_absent(self):
        """
        Verify that character limit UI elements are NOT rendered when CHARACTER_LIMIT is None.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')

        self.assertNotIn('maxlength="', content)
        self.assertNotIn('0/', content)

    def test_password_toggle_elements_exist(self):
        """Verify that the password toggle button and wrapper exist in the HTML."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for the wrapper with relative positioning
        self.assertIn('style="position: relative;"', html)

        # Check for the password input with padding
        self.assertIn('style="padding-right: 40px;"', html)

        # Check for the toggle button
        self.assertIn('onclick="togglePassword(this, \'password\')"', html)
        self.assertIn('aria-label="Show password"', html)
        self.assertIn('title="Show password"', html)
        self.assertIn('👁️', html)

        # Check for the JS function
        self.assertIn('function togglePassword(btn, inputId)', html)
        self.assertIn("btn.setAttribute('title', 'Hide password')", html)
        self.assertIn("btn.setAttribute('title', 'Show password')", html)

    def test_textarea_resize_behavior(self):
        """Verify the textarea resize behavior in CSS and auto-resize JS."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for CSS changes
        self.assertIn('resize: none', html)
        self.assertIn('overflow-y: hidden', html)

        # Check for JS changes
        self.assertIn('const autoResize = () => {', html)
        self.assertIn('textarea.addEventListener(\'input\', autoResize);', html)

    def test_admin_password_toggle_exists(self):
        """Verify that the admin password toggle button exists in the History HTML."""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for the toggle button which is unique by its onclick handler
        self.assertIn("togglePassword(this, 'admin_password')", html)
        self.assertIn('aria-label="Show password"', html)
        self.assertIn('title="Show password"', html)
        self.assertIn('👁️', html)

    def test_history_page_ux(self):
        """Verify UX enhancements on the History page."""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for auto-focus on admin password input
        self.assertIn("const pwInput = document.getElementById('admin_password');", html)
        self.assertIn("pwInput.focus();", html)

        # Check for form submission loading state logic
        self.assertIn("document.querySelectorAll('form').forEach(form => {", html)
        self.assertIn("form.addEventListener('submit', function(e) {", html)
        self.assertIn("if (this.action.includes('download-csv')) return;", html)
        self.assertIn("Verifying... ⏳", html)

    def test_focus_visible_styles_present(self):
        """Verify that :focus-visible styles are defined in CSS for keyboard accessibility."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for the specific CSS rule we added
        self.assertIn('button:focus-visible, a:focus-visible', html)
        self.assertIn('box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5)', html)

    def test_button_hover_and_disabled_styles(self):
        """Verify that danger buttons have hover states and disabled states apply universally."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for danger button hover state
        self.assertIn('.btn-danger:hover { background-color: var(--danger-hover); }', html)

        # Check for universal disabled button state
        self.assertIn('.btn:disabled { background-color: var(--border); cursor: not-allowed; color: var(--text-muted); }', html)

    def test_os_aware_keyboard_shortcut_logic(self):
        """Verify that OS-aware keyboard shortcut logic exists in SHARED_JS."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        self.assertIn("navigator.userAgent.toLowerCase().includes('mac')", html)
        self.assertIn("<kbd>⌘ Cmd</kbd> + <kbd>Enter</kbd>", html)

    def test_semantic_landmarks(self):
        """Verify that semantic <main> tags are used instead of <div class='container'>."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('<main class="container">', html)
        self.assertNotIn('<div class="container">', html)

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('<main class="container" style="max-width: 900px;">', html)
        self.assertNotIn('<div class="container" style="max-width: 900px;">', html)

    def test_admin_password_autocomplete(self):
        """Verify that the admin password field has the autocomplete attribute."""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('autocomplete="current-password"', html)


    def test_scrollable_table_ux(self):
        """Verify that scrollable tables have sticky headers and accessibility attributes."""
        # Check history HTML structure by simulating login
        from app import ADMIN_PASSWORD
        response = self.client.post('/history', data={'admin_password': ADMIN_PASSWORD})
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')

        # Check for sticky th
        self.assertIn('position: sticky; top: 0; z-index: 10;', html)

        # Check for role region and tabindex
        self.assertIn('role="region"', html)
        self.assertIn('tabindex="0"', html)
        self.assertIn('aria-label="Print history"', html)

        # Check for :focus-visible style for [role="region"]
        self.assertIn('[role="region"]:focus-visible', html)

    def test_decorative_emoji_hidden(self):
        """Verify that decorative emojis are hidden from screen readers."""
        response = self.client.get('/')
        html = response.data.decode('utf-8')
        self.assertIn('<span aria-hidden="true">📠</span>', html)

        response = self.client.get('/history')
        html = response.data.decode('utf-8')
        self.assertIn('<span aria-hidden="true">📜</span>', html)

    def test_history_unauthenticated_escape_hatch(self):
        """Verify that the 'Back to Portal' link is present for unauthenticated users."""
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('<a href="/" class="btn btn-secondary">Back to Portal</a>', html)


if __name__ == '__main__':

    unittest.main()
