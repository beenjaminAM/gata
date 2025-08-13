from playwright.sync_api import sync_playwright
import time
#https://d-cf.inkabetplayground.net/stc-943713193/stc-943713193
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto("https://inkabet.pe/pe/apuestas-deportivas/")  #iframe #document.querySelector('#loader').nextElementSibling.getAttribute('src')

        # Wait until the loading spinner (#loader) is hidden
        page.wait_for_function("""
            () => {
                const loading = document.querySelector('#loader');
                if (!loading) return false;
                const style = loading.style.display;
                if (!style.includes('none')) return false;
                return true;
            }
        """)

        page.wait_for_selector("iframe#sportsBookIframe")
        iframe_element = page.query_selector("iframe#sportsBookIframe")
        iframe_src = iframe_element.get_attribute("src")

        print(f"URL: {iframe_src}")

        # Open iframe URL in a new tab
        new_page = context.new_page()
        new_page.goto(iframe_src)

        # Zoom out the page and hide unnecessary UI elements to ensure that all dynamic content is fully loaded and visible in the DOM.
        new_page.evaluate("document.body.style.zoom=0.6")
        time.sleep(0.7)
        button1 = new_page.get_by_role("button", name="Ocultar deportes")
        if button1.is_visible():
            button1.click()

        time.sleep(0.5)  # Slight delay to let the UI update
        button2 = new_page.get_by_role("button", name="Ocultar cupón de apuestas")
        if button2.is_visible():
            button2.click()
        new_page.wait_for_selector(".obg-scroller .obg-scroller-container .obg-scroller-content")

        scroller_items = new_page.eval_on_selector(
            ".obg-scroller .obg-scroller-container .obg-scroller-content",
            """container => Array.from(container.children).map(el => el.innerText.trim())"""
        )
        print(scroller_items)

        def select_league(new_page, league):
            found = new_page.evaluate("""
                (league)=> {
                    let result = Array.from(document.querySelector('.obg-scroller .obg-scroller-container .obg-scroller-content').children).find(el=>el.innerText.toLowerCase().includes(league.toLowerCase()))
                    if (result) result.click();
                    return !!result;
                }
            """, arg=league)
            if not found:
                raise Exception('League not Found')
            
        select_league(new_page, 'liga 1')
        try: 
            league = new_page.locator('xpath=//html/body/app-root/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')#iframe -> events
            new_page.wait_for_timeout(4000)
            dates = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    return Array.from(getElementByXpath('/html/body/app-root/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).map(el=>el?.querySelector('.obg-uiuplift-accordion-item-header')?.innerText?.trim().replace(/\\n/g, '') || null);
                }
            """)

            print(dates)
            array_dates = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    const league = getElementByXpath('/html/body/app-root/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')
                    
                    league.querySelector('.obg-scrollbar-content').scrollTop = league.querySelector('.obg-scrollbar-content').scrollHeight
                    
                    const dates = Array.from(league?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []);
                    const result = dates.map(cont => {
                        let events_date = cont?.querySelector('.obg-uiuplift-accordion-item-header')?.innerText?.replace(/\\u00A0/g, ' ').trim().replace(/\\n/g, '') || null;
                        
                        let events = Array.from(cont?.querySelectorAll('.obg-event-table-container > *:not(div)')); //calentar -> days -> event
                        events_array = events.map(data => {
                            let event_details = data.querySelector('a.obg-event-row-details'); // match details (teams and time)
                            let participants_names = Array.from(event_details.querySelectorAll('.obg-event-scorecard-participants-name')).map(el => el.innerText);
                            let date_time = event_details.querySelector('time')?.innerText // will return null on live matches
                            const betting = data.querySelectorAll('.obg-event-row-wrapper')
                            let home_team = betting[0].querySelectorAll('.obg-selection-v2-label')[0]?.innerText
                            let away_team = betting[0].querySelectorAll('.obg-selection-v2-label')[2]?.innerText
                            let home_win_odds = betting[0].querySelectorAll('.obg-selection-base-odds')[0]?.innerText
                            let draw_odds     = betting[0].querySelectorAll('.obg-selection-base-odds')[1]?.innerText
                            let away_win_odds = betting[0].querySelectorAll('.obg-selection-base-odds')[2]?.innerText
                            let test = {
                                "home_team": "Sport Boys Association",
                                "away_team": "Deportivo Garcilaso",
                                "home_win_odds": 1.88,
                                "draw_odds": 3.50,
                                "away_win_odds": 3.90
                            }
                            test = {
                                "total_goals_market": "2.5",
                                "over_2_5_goals_odds": 1.95,
                                "under_2_5_goals_odds": 1.82
                            }
                            total_goals_market = betting[1].querySelectorAll('.obg-selection-v2-label-wrapper.horizontal')[0]?.innerText.split('de ')[1] // más de 2.5
                            over_goals_market_odds  = betting[1].querySelectorAll('.obg-selection-base-odds')[0]?.innerText
                            under_goals_market_odds = betting[1].querySelectorAll('.obg-selection-base-odds')[1]?.innerText
                            betting[2] // european handicap
                            betting[3] // both teams score
                            let both_teams_to_score_yes = betting[3].querySelectorAll('.obg-selection-base-odds')[0].innerText
                            let both_teams_to_score_no  = betting[3].querySelectorAll('.obg-selection-base-odds')[1].innerText
                            let matchObject = {
                                date_time: date_time,
                                home_team: home_team,
                                away_team: away_team,
                                odds: {
                                    match_result: {
                                        home_win: home_win_odds,
                                        draw: draw_odds,
                                        away_win: away_win_odds
                                    },
                                    total_goals: {
                                        market: total_goals_market,
                                        over: over_goals_market_odds,
                                        under: under_goals_market_odds
                                    }
                                }
                            };
                            return matchObject
                                            
                        })
                        return events_array
                    })
                                        
                    return result;

                }
            """)

            print(array_dates)
            
            events = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    const league = getElementByXpath('/html/body/app-root/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')
                    league.querySelector('.obg-scrollbar-content').scrollTop = league.querySelector('.obg-scrollbar-content').scrollHeight
                    let events = Array.from(league?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).map(el => Array.from(el.querySelectorAll('a.obg-event-row-details'))).flat(1).map(el => el.querySelector('.obg-event-scorecard-labels').innerText.concat(' ', el.querySelector('.obg-event-info-header .obg-event-status').innerText));
                    return events;
                }
            """)
            print('Fire')
            for event in events:
                print(event)
        except Exception as e:
            print("⚠️ Error locating event container:", e)

        page.wait_for_timeout(15000)
        context.close()
        browser.close()

if __name__ == "__main__":
    run()
