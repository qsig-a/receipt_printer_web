from playwright.sync_api import sync_playwright

def verify_404_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to a non-existent page
        response = page.goto("http://localhost:5000/this-page-does-not-exist")

        # response.status is a property in some versions or method in others, checking docs usually helps but let's assume property if method fails
        # Actually in playwright python it is a method but I might have used it wrong.
        # Wait, response.status() is correct for Playwright Python.
        # Ah, the error says 'int' object is not callable. So response.status is an int property?
        # Let's check: https://playwright.dev/python/docs/api/class-response#response-status
        # It is a method.
        # Wait, maybe I'm using an older version where it was a property?
        # Let's try accessing it as a property just in case.

        status = response.status if isinstance(response.status, int) else response.status()
        print(f"Status code: {status}")

        # Take a screenshot
        page.screenshot(path="verification/404_page.png")

        browser.close()

if __name__ == "__main__":
    verify_404_page()
