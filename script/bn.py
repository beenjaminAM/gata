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
    
    try:
        if page.locator("#landing-page-modal").is_visible(timeout=3000):
            page.locator("#landing-page-modal").get_by_role("button").click()
    except Error:
        print("Modal not visible")

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
    try:
        select_league(page, "Premier League")  # Replace with the league you want
        print("League selected successfully.")
    except Exception as err:
        print(err)
    page.wait_for_timeout(2000)
    print(leagues)
    # This uses a CSS attribute selector to select all elements where the attribute data-qa starts with the string "match_day_".
    # tw-border-solid tw-border-n
    list_data = page.evaluate("""
            () => {
                result = []
                const rawMatches = Array.from(document.querySelectorAll("[data-qa^='match_day_'] > div > div > div"));
                              
                result = rawMatches.map((rawMatchData) => {
                    const matchData = { }
                    const rawFields = Array.from(rawMatchData?.querySelectorAll(":scope > div")).slice(0,3); 
                    matchData['date'] = rawFields[0].innerText.trim().replace('\\n', ' ');
                    const event_match = rawFields[1].innerText.split('\\n').slice(0,2);
                    [matchData['home'], matchData['visit']] = event_match;
                    const event_match_odds = rawFields[2].firstElementChild.querySelectorAll(':scope > div > span:last-child')
                    const odds_array = Array.from(event_match_odds).map(el=>el.innerText.trim());
                    [matchData['home_odds'], matchData['draw'], matchData['visit_odds']] = odds_array;
                    let matchObject = {
                        date_time: matchData['date'],
                        home_team: matchData['home'],
                        away_team: matchData['visit'],
                        odds: {
                            match_result: {
                                home_win: matchData['home_odds'],
                                draw: matchData['draw'],
                                away_win: matchData['visit_odds']
                            }
                        }
                    };      
                    return matchObject
                })
                return result
            }
        """)
    print(list_data)
    import json
    print(json.dumps(list_data, indent=4, ensure_ascii=False))

    page.wait_for_timeout(15000)
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)