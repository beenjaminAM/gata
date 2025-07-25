from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto("https://inkabet.pe/pe/apuestas-deportivas/")

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

        new_page.wait_for_selector(".obg-scroller .obg-scroller-container .obg-scroller-content")

        scroller_items = new_page.eval_on_selector(
            ".obg-scroller .obg-scroller-container .obg-scroller-content",
            """container => Array.from(container.children).map(el => el.innerText.trim())"""
        )

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
                    return Array.from(getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).map(el=>el?.querySelector('.obg-uiuplift-accordion-item-header')?.innerText?.trim().replace(/\\n/g, '') || null);
                }
            """)
            array_dates = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    const league = getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')
                    
                    league.querySelector('.obg-scrollbar-content').scrollTop = league.querySelector('.obg-scrollbar-content').scrollHeight
                    
                    const dates = Array.from(league?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []);
                    const result = dates.map(cont => {
                        let events_date = cont?.querySelector('.obg-uiuplift-accordion-item-header')?.innerText?.replace(/\\u00A0/g, ' ').trim().replace(/\\n/g, '') || null;
                        
                        let events = Array.from(cont?.querySelectorAll('.obg-event-table-container > *:not(div)'));
                        events_array = events.map(data => {
                            let event_details = data.querySelector('a.obg-event-row-details');
                            let participants_names = Array.from(event_details.querySelectorAll('.obg-event-scorecard-participants-name')).map(el => el.innerText);
                            let parts_odds = Array.from(data.querySelectorAll('.obg-selection-base.genos-interactive.ng-star-inserted')).map(el => el.innerText.replace('\\n', '-'))
                            return {"date": events_date, "parts": participants_names, "odds": parts_odds}
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
                    const league = getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')
                    league.querySelector('.obg-scrollbar-content').scrollTop = league.querySelector('.obg-scrollbar-content').scrollHeight
                    let events = Array.from(league?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).map(el => Array.from(el.querySelectorAll('a.obg-event-row-details'))).flat(1).map(el => el.querySelector('.obg-event-scorecard-labels').innerText.concat(' ', el.querySelector('.obg-event-info-header .obg-event-status').innerText));
                    return events;
                }
            """)
            for event in events:
                print(event)
        except Exception as e:
            print("⚠️ Error locating event container:", e)

        page.wait_for_timeout(30000)
        context.close()
        browser.close()

if __name__ == "__main__":
    run()
