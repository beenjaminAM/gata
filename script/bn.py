
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.betano.pe/sport/futbol/") 
        
    # Wait until the loading spinner (#loader) is hidden
    page.wait_for_function("""
        () => {
            let leagues = document.querySelectorAll('.swiper-wrapper')[1]?.children;
            if (!leagues) return false;
            return true;
        }
    """, timeout= 60000)
    leagues = page.evaluate("""
        () => {
            let leagues = document.querySelectorAll('.swiper-wrapper')[1].children;
            return Array.from(leagues).map(el => el.querySelector('span').innerText);
        }
    """)
    print(leagues)

    page.wait_for_timeout(15000)
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)