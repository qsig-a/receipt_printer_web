from playwright.sync_api import sync_playwright, expect
import time
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("Navigating to app...")
    page.goto("http://localhost:5000")

    # Test PRINT_SUCCESS
    print("Testing PRINT_SUCCESS...")
    page.fill("input[name='password']", "password") # Default password in mock_app
    page.fill("textarea[name='message']", "Success Message")
    page.click("button[type='submit']")

    # Wait for status box
    status_box = page.locator(".status-box")
    expect(status_box).to_be_visible()

    # Check for correct data-code and class
    expect(status_box).to_have_attribute("data-code", "PRINT_SUCCESS")
    expect(status_box).to_have_class("status-box status-success")

    # Check title and message
    title = status_box.locator(".status-title")
    expect(title).to_have_text("Success")
    message = status_box.locator(".status-message")
    expect(message).to_have_text("Message sent to printer.")

    page.screenshot(path="verification_success_refined.png")
    print("Screenshot saved: verification_success_refined.png")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
