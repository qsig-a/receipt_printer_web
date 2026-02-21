from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()

    # Go to history page
    page.goto("http://localhost:5000/history")

    # Login
    page.fill("input[name='admin_password']", "adminpassword")
    page.click("button:text('View Logs')")

    # Wait for admin actions
    page.wait_for_selector(".admin-actions")

    # Measure buttons
    csv_btn = page.locator("form[action='/download-csv'] button")
    clear_btn = page.locator("form[action='/clear-history'] button")

    csv_box = csv_btn.bounding_box()
    clear_box = clear_btn.bounding_box()

    print(f"CSV Button: {csv_box}")
    print(f"Clear Button: {clear_box}")

    if csv_box['width'] == clear_box['width'] and csv_box['height'] == clear_box['height']:
        print("Buttons are exactly the same size.")
    else:
        print("Buttons are DIFFERENT sizes.")

    page.screenshot(path="verification_history_buttons_check.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
