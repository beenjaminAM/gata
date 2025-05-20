from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://inkabet.pe/pe/apuestas-deportivas/")

        # Wait until the loading spinner (#loader) is hidden
        page.wait_for_function("""
            () => {
                const loading = document.querySelector('#loader');
                if (!loading) return false;
                const style = loading?.style?.display
                if (!loading?.style?.display.includes('none')) return false;
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

        scroller_items = new_page.eval_on_selector_all(
            ".obg-scroller .obg-scroller-container .obg-scroller-content > *",
            "elements => elements.map(el => el.innerText.trim())"
        )

        new_page.evaluate("""
            ()=> {
                Array.from(document.querySelector('.obg-scroller .obg-scroller-container .obg-scroller-content').children).find(el=>el.innerText.toLowerCase().includes('liga 1')).click()
            }
        """)

        try: 
            league = new_page.locator('xpath=//html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')#iframe -> events
            new_page.wait_for_timeout(4000)
            dates = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    return Array.from(getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).map(el=>el?.querySelector('.obg-uiuplift-accordion-item-header')?.innerText?.trim().replace(/\\n/g, '') || null);
                }
            """)
            
            events = new_page.evaluate("""
                () => {
                    function getElementByXpath(path) {
                        return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    const league = getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')
                    league.querySelector('.obg-scrollbar-content').scrollTop = league.querySelector('.obg-scrollbar-content').scrollHeight
                    let events = Array.from(getElementByXpath('/html/body/app-root/obg-m-betting-layout-container/obg-m-sportsbook-layout-container/app-m-sidenav/mat-sidenav-container/mat-sidenav-content/div')?.querySelectorAll('obg-uiuplift-accordion > :not(div)') || []).flatMap(el => Array.from(el?.querySelector('.obg-uiuplift-accordion-item-content')?.querySelector('.obg-event-table-container')?.querySelectorAll('a.obg-event-row-details') || []).map(a => a.querySelector('div.obg-event-scorecard-labels.event-table.ng-star-inserted')).filter(Boolean));
                    return events.map(el => el.innerText)
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
