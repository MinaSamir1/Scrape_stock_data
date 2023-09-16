from playwright.async_api import Playwright, async_playwright
import pandas as pd
import asyncio
import json

WEB_SOCKET_NUM = 0
DATA = pd.DataFrame()


def get_IQ_option_stock(payload):
    try:
        payload = eval(payload)
        frame = payload['msg']['candles']
        df = pd.DataFrame(frame)
        print('GET DATA:', len(df))
        return df
    except Exception as e:
        return None


async def save_socket_data(payload):
    try:
        global WEB_SOCKET_NUM, DATA
        WEB_SOCKET_NUM += 1

        df = get_IQ_option_stock(payload)
        
        if df is not None:
            DATA = pd.concat([DATA, df])
            print('DATA:', len(DATA))
            print('DATA ADDED\n')
            WEB_SOCKET_NUM = 0            

    except Exception as e:
        print("FAILD EXCEPTION: " , e)


async def on_web_socket(ws):
    print(f"WebSocket opened: {ws.url}")
    ws.on("framereceived",     lambda payload: save_socket_data(payload))


async def run(playwright: Playwright) -> None:

    browser = await playwright.firefox.launch_persistent_context(user_data_dir='chrome', headless=False)
    page = browser.pages[0]

    await page.goto("https://km.iqoption.com/traderoom", timeout=50000)
    viewport_size = page.viewport_size
    screen_width  = viewport_size['width']
    screen_height = viewport_size['height']
    print(f"Screen size: {screen_width}x{screen_height}")
    page.on("websocket", on_web_socket)


    while True:
        await page.mouse.move(screen_width/2 - 400, screen_height/2)
        await page.mouse.down()
        await page.mouse.move(screen_width/2 + 300, screen_height/2)
        await page.mouse.up()

        if  WEB_SOCKET_NUM >= 500:
            print('\n**********',WEB_SOCKET_NUM)
            DATA.to_csv('data.csv')
            break

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())