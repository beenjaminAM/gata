from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError

def wait_for_shadow_dom_ready(page):
    try:
        page.wait_for_function("""
            () => {
                const host = document.querySelector('#altenar-wrapper__sportbook');
                if (!host || !host.childNodes.length) return false;
                const shadowRoot = host.childNodes[0].shadowRoot;
                if (!shadowRoot || !shadowRoot.childNodes.length) return false;
                return true;
            }
        """)
    except PlaywrightTimeoutError:
        raise Exception('Waiting took too long')

def inspect_shadow_dom_content(page):
        test = page.evaluate("""
            () => {
                let test  = []
                const content = document.querySelector('#altenar-wrapper__sportbook').childNodes[0].shadowRoot.childNodes[0];
                if (content) test.push('content');
                //const boxes = content.querySelectorAll('div.TopLeaguesstyled__TopLeagueBox-sc-1okpmvu-5.dxQYeD')
                const boxes = content.querySelectorAll('div.TopLeaguesstyled__TopLeagueBox-sc-1okpmvu-5.bGLWSD');
                if (boxes.length) test.push('leagues');
                return test;
            }
        """)
        print(test)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=None)
    page = context.new_page()

    page.goto("https://www.apuestatotal.com/apuestas-deportivas/#/overview")
    
    page.wait_for_selector("#altenar-wrapper__sportbook")

    wait_for_shadow_dom_ready(page)

    def click_menu_in_page(league):
        page.wait_for_function("""
            (league) => {

                const content = document.querySelector('#altenar-wrapper__sportbook').childNodes[0].shadowRoot.childNodes[0];
                if (!content) return false;

                //const boxes = content.querySelectorAll('div.TopLeaguesstyled__TopLeagueBox-sc-1okpmvu-5.dxQYeD');
                const boxes = content.querySelectorAll('.TopLeaguesstyled__TopLeagueName-sc-1okpmvu-6');
                if (!boxes.length) return false;

                const target = Array.from(boxes).find(div => div.innerText.includes(league));
                if (target) {
                    target.click();
                    return true;
                }

                return false;
            }
        """, arg=league)
    
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
                
                return Array.from(event_boxes).map(div => {
                    const [home, visit] = Array.from(div.querySelectorAll('.EventBoxCompetitorsVariant0styled__CompetitorContainer-sc-nkyjoa-5')).slice(0, 2)
                    const date = div.querySelector('.EventBoxstyled__DateTime-sc-ksk2ut-8')
                    const category = div.querySelector('.EventBoxstyled__CategoryChampionship-sc-ksk2ut-6')
                    const raw = Array.from(div.querySelectorAll('.OddBoxVariant2styled__OddBoxContent-sc-9pzo4l-2'))
                    const values = raw.reduce((acc,item) => {
                        const [value, key] = item.innerText.split('\\n')
                        acc[key] = value
                        return acc
                    }, { })
                    values['date'] = date.innerText
                    values['category'] = category.innerText
                    values['home'] = home.innerText
                    values['visit'] = visit.innerText
                    return values
                }) 
            }
        """)
        print(list_data)

        with open("matches.json", "w", encoding="utf-8") as f:
            import json
            json.dump(list_data, f, ensure_ascii=False, indent=4)
        
        #event_boxes.map(div -> div.innertText):list, [slip] for item in list = ['10/05 • 21:00', 'Liga 1 • Perú', 'Cienciano', 'FBC Melgar', '2.85', 'Cienciano', '3.20', 'Empate', '2.54', 'FBC Melgar', '1.94', 'Más de 2.5', '1.80', 'Menos de 2.5', '1.70', 'Sí', '2.05', 'No']


    click_menu_in_page('Brasileirao')

    events_data_in_page()

    #page.wait_for_timeout(30000)

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)