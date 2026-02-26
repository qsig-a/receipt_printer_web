from playwright.sync_api import sync_playwright

def verify_history_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Navigate to History Page (using port 5001)
        print("Navigating to history page...")
        page.goto("http://localhost:5001/history")

        # 2. Check Auto-Focus
        print("Checking auto-focus...")
        focused_element = page.evaluate("document.activeElement.id")
        print(f"Focused element ID: {focused_element}")

        if focused_element != "admin_password":
            print("❌ FAILURE: Admin password input is NOT focused.")
        else:
            print("✅ SUCCESS: Admin password input IS focused.")

        # 3. Take Screenshot of History Page (Login)
        page.screenshot(path="verification/history_login.png")
        print("Screenshot saved to verification/history_login.png")

        # 4. Attempt Login to View History
        print("Attempting login...")
        page.fill("#admin_password", "adminpassword")

        # 5. Verify Button Loading State
        # We'll attach a listener to print the button text when it changes
        page.evaluate("""
            const btn = document.querySelector('button[type="submit"]');
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        console.log('Button text changed to:', btn.innerText);
                    }
                });
            });
            observer.observe(btn, { childList: true });
        """)

        # Click submit
        page.click("button[type='submit']")

        # Wait for navigation
        page.wait_for_load_state("networkidle")

        # 6. Take Screenshot of History Page (Logged In)
        page.screenshot(path="verification/history_logged_in.png")
        print("Screenshot saved to verification/history_logged_in.png")

        browser.close()

if __name__ == "__main__":
    verify_history_page()
