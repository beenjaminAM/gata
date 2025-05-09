from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=None)
    page = context.new_page()

    page.goto("https://www.apuestatotal.com/apuestas-deportivas/#/overview")
    
    page.wait_for_selector("#altenar-wrapper__sportbook")

    # Wait until shadow DOM is fully ready
    page.wait_for_function("""
        () => {
            const host = document.querySelector('#altenar-wrapper__sportbook');
            if (!host || !host.childNodes.length) return false;
            const shadowRoot = host.childNodes[0].shadowRoot;
            if (!shadowRoot || !shadowRoot.childNodes.length) return false;
            return true;
        }
    """)

    def click_menu_in_page(league):
        page.wait_for_function("""
            (league) => {

                const content = document.querySelector('#altenar-wrapper__sportbook').childNodes[0].shadowRoot.childNodes[0];
                if (!content) return false;

                const boxes = content.querySelectorAll('div.TopLeaguesstyled__TopLeagueBox-sc-1okpmvu-5.dxQYeD');
                if (!boxes.length) return false;

                const target = Array.from(boxes).find(div => div.innerText.includes(league));
                if (target) {
                    target.click();
                    return true;
                }

                return false;
            }
        """, arg="Liga 1")
    
    def events_data_in_page():
        page.wait_for_function("""
            () => {


                const content = document.querySelector('#altenar-wrapper__sportbook').childNodes[0].shadowRoot.childNodes[0];
                if (!content) return false;

                const boxes = content.querySelectorAll('div.EventBoxstyled__EventBoxContainerBase-sc-ksk2ut-33.EventBoxVariant0styled__EventBoxContainer-sc-32j3jk-0.cKTlxT.hsDHkP');
                if (!boxes.length) return false;
           
                return true;
            }
        """)

        list_data = page.evaluate("""
            () => {
                const host = document.querySelector('#altenar-wrapper__sportbook');
                const shadowRoot = host.childNodes[0].shadowRoot;
                const content = shadowRoot.childNodes[0];

                const event_boxes = content.querySelectorAll('div.EventBoxstyled__EventBoxContainerBase-sc-ksk2ut-33.EventBoxVariant0styled__EventBoxContainer-sc-32j3jk-0.cKTlxT.hsDHkP');
                return Array.from(event_boxes).map(div => div.innerText);
            }
        """)
        list_data = [[info.strip() for info in data.strip().split('\n')] for data in list_data]


        print(list_data)

    click_menu_in_page('Liga 1')

    events_data_in_page()

    #page.wait_for_timeout(30000)

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)