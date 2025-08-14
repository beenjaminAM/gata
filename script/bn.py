from playwright.sync_api import Playwright
from patchright.sync_api import sync_playwright
import os

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    
    auth_dir = os.path.join(os.getcwd(), 'playwright', '.auth')
    os.makedirs(auth_dir, exist_ok=True)
    state_path = os.path.join(auth_dir, "state_testing1.json")

    # Check if auth state already exists
    if os.path.exists(state_path):
        context = browser.new_context(storage_state=state_path, no_viewport=True)
    else:
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", no_viewport=True)
        page = context.new_page()
        page.goto("https://www.betano.pe/sport/futbol/")
        input("Complete the walkthrough and accept cookies, then press Enter...")
        context.storage_state(path=state_path)

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
    def select_league(page, league):
        try:
            # Click element
            result = page.evaluate("""
                (league) => {
                    let leagues = document.querySelectorAll('.swiper-wrapper')[1]?.children;
                    if (!leagues) throw new Error('League container not found');

                    let league_el = Array.from(leagues).find(el => el.querySelector('span')?.innerText.toLowerCase() === league.toLowerCase());
                    if (!league_el) throw new Error(`League '${league}' not found`);

                    league_el.firstElementChild?.click();
                    return true;
                }
            """, arg=league)

            # Wait for the element to be marked as active
            page.wait_for_function("""
                (league) => {
                    let leagues = document.querySelectorAll('.swiper-wrapper')[1]?.children;
                    let league_el = Array.from(leagues).find(el => el.querySelector('span')?.innerText.toLowerCase() === league.toLowerCase());
                    let classList = league_el?.firstElementChild?.classList;

                    if (!classList) return false;
                    return classList.contains('tw-border-solid') && classList.contains('tw-border-n');
                }
            """, arg=league, timeout=5000)  # Optional: Set a timeout (in ms)

        except Exception as e:
            raise Exception(f"Failed to select league '{league}': {str(e)}")
    select_league(page, "Copa Libertadores")
    page.wait_for_timeout(2000)
    print(leagues)
    list_data = page.evaluate("""
            () => {
                const result = { }
                const rawMatches = document.querySelectorAll("[data-qa^='match_day_'] > div > div");
                const rawFields = Array.from(rawMatches[0].firstElementChild?.querySelectorAll(":scope > div:not(.v-popper--theme-dropdown)")).slice(0,3); 
                result['date'] = rawFields[0].innerText.trim().replace('\\n', ' ');
                const event_match = rawFields[1].innerText.split('\\n').slice(0,2);
                [result['home'], result['visit']] = event_match;
                const event_match_odds = rawFields[2].firstElementChild.querySelectorAll(':scope > div > span:last-child')
                const odds_array = Array.from(event_match_odds).map(el=>el.innerText.trim());
                [result['home_odds'], result['draw'], result['visit_odds']] = odds_array;
                return result
            }
        """)
    print(list_data)

    page.wait_for_timeout(15000)
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)