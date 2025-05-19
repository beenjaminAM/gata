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

        print("items:")
        for item in scroller_items:
            print("-", item)


        page.wait_for_timeout(30000)
        context.close()
        browser.close()

if __name__ == "__main__":
    run()
