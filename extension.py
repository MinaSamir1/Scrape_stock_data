from playwright.sync_api import sync_playwright
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from pathlib import Path


with sync_playwright() as playwright:

    context = playwright.firefox.launch_persistent_context('VPN_test',
        headless=False,

        #args=[
        #f"--headless=new",
        #f"--disable-extensions-except={path_to_extension}",
        #f"--load-extension={path_to_extension}",
        #],
    )

    context.set_default_timeout(100000)
    print(context.background_pages, context.pages)
    page = context.pages[0]
    time.sleep(3)

    ### **************************************************************************
    
    page.goto("https://mylocation.org")
    page.wait_for_load_state("load")
    
    _ = input('Press Enter to start')
    print(context.background_pages, context.pages)
    content = page.query_selector('body')
    print('*'*50, '/n')
    all = content.query_selector_all(':scope > *')

    print(len(all))

    for i in all:
        print(i.inner_text().splitlines())                
        parent_element = i.evaluate_handle('(element) => element.cloneNode(false)')
        parent_text    = page.evaluate('(element) => element.innerText', parent_element)

        print('*'*50)
    
    _ = input("Press any key to exist...")
    context.close()

