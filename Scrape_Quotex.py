from playwright.async_api import Playwright, async_playwright
import pandas as pd
import asyncio

WEB_SOCKET_NUM = 0
DATA = []


def get_quotex_stock_data(payload):
    try:
        stock = eval(payload.decode('utf-8')[1:])
        df = pd.DataFrame(stock['data'])
        print('GET DATA:', len(df))
        return df
    except Exception as e:
        return None


async def save_socket_data(payload):
    try:
        global WEB_SOCKET_NUM, DATA
        WEB_SOCKET_NUM += 1
        df = get_quotex_stock_data(payload)
        
        if df is not None:
            DATA.append(df)
            print('DATA:', len(DATA))
            
            if len(DATA) == 5:
                df = pd.concat(DATA)
                df.to_csv(f'Quotex_stock/data{WEB_SOCKET_NUM}.csv', index=False)
                DATA = []
                print('=====> SAVED DATA:\n')

    except Exception as e:
        print("FAILD EXCEPTION: " , e)


async def on_web_socket(ws):
    print(f"WebSocket opened: {ws.url}")
    ws.on("framereceived",     lambda payload: save_socket_data(payload))


async def run(playwright: Playwright) -> None:

    browser = await playwright.firefox.launch_persistent_context(user_data_dir='chrome', headless=False)
    page = browser.pages[0]
    page.on("websocket", on_web_socket)
    await page.goto("https://qxbroker.com/en/trade", timeout=50000)

    viewport_size = page.viewport_size
    screen_width  = viewport_size['width']
    screen_height = viewport_size['height']
    print(f"Screen size: {screen_width}x{screen_height}")


    while True:
        await asyncio.sleep(0.5)
        await page.mouse.down()
        await page.mouse.move(screen_width/2 - 400, screen_height/2)
        await page.mouse.move(screen_width/2 + 300, screen_height/2)
        await page.mouse.up()

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
