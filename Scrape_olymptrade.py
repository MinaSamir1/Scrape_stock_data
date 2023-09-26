from playwright.async_api import Playwright, async_playwright
from playwright_stealth import stealth_async
import pandas as pd
import asyncio
import json
import os 

WEB_STOCK_NUM = 0
DATA = pd.DataFrame()


### Get the stock data and get the data in the dataframe
def get_olymptrade_stock_data(stock):
    try:
        stock = json.loads(stock)
        df = pd.DataFrame(stock[0]['d'][0]['candles'])
        #print('GET DATA:', len(df), end='\r')
        return df
    except Exception as e:
        return None


### the Callable function to save the stock data in receive frames 
async def save_stock_data(payload):
    try:
        global WEB_STOCK_NUM, DATA
        WEB_STOCK_NUM += 1
        df = get_olymptrade_stock_data(payload)
        
        if df is not None:
            DATA = pd.concat([DATA, df])
            print('DATA:', len(DATA), end='\r')
            #print('DATA ADDED\n')
            WEB_STOCK_NUM = 0

    except Exception as e:
        print("FAILD EXCEPTION: " , e)


### the EVENT function to get the receive frames
async def on_web_socket(ws):
    print(f"WebSocket opened: {ws.url}")
    ws.on("framereceived", lambda payload: save_stock_data(payload))


### Scrape the stock data by get load the history data in page
async def get_stock_data(page, stock_title):
    global DATA, WEB_STOCK_NUM

    screen_width  = page.viewport_size['width']
    screen_height = page.viewport_size['height']
    #print(f"Screen size: {screen_width}x{screen_height}")
    print(f"\nGet stock: {stock_title}")

    while True:
        await page.mouse.move(screen_width/2 - 400, screen_height/2)
        await page.mouse.down()
        await page.mouse.move(screen_width/2 + 300, screen_height/2)
        await page.mouse.up()

        if  WEB_STOCK_NUM >= 200:
            stock_title = stock_title[:-3].replace('/', '_')
            DATA.to_csv(f'olymptrade_stock/{stock_title}.csv')
            print('\n**********',WEB_STOCK_NUM)
            break

    WEB_STOCK_NUM = 0
    DATA = pd.DataFrame()


async def run(playwright: Playwright) -> None:

    browser = await playwright.firefox.launch_persistent_context(user_data_dir='chrome', headless=False)

    page = browser.pages[0]
    await stealth_async(page)

    
    page.on("websocket", on_web_socket)
    await page.goto("https://olymptrade.com/platform", timeout=50000)
    #_ = input('Press Enter to continue...')

    #### Get the Stock 
    for count in range(1000):
        await page.locator('button[data-test="asset-select-button"]').click()
        stock = page.locator('div[data-test="asset-item"]').nth(count)
        stock_title = await stock.text_content()
        await stock.click()
        await page.locator('button[data-test="cor-w-panel-close"]').click()
        
        await page.locator('//*[@id="chart-6ae54"]/div[1]/ul/li[2]/div/div/span/button').dispatch_event('click') ### Open the chart type
        await page.locator('//*[@id="chart-6ae54"]/div[1]/ul/li[2]/div/div[1]/div/div/div/button[2]').click() ### Get the candles 
        
        await page.locator('//*[@id="chart-6ae54"]/div[2]/div/div/div/span/button').dispatch_event('click')  ## Get the time intervals
        await page.locator('//*[@id="chart-6ae54"]/div[2]/div/div/div[1]/div/div/div/button[1]').dispatch_event('click') ### Get the 5S 

        for i in range(3):
            await page.locator('//*[@id="chart-6ae54"]/div[2]/div/button[1]').click() ### Zoom out the page
        
        print('start get stock data')
        await get_stock_data(page, stock_title)
        print('\n')

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
