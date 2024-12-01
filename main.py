import asyncio 
from playwright.async_api import async_playwright, PlaywrightContextManager, Response
from bs4 import BeautifulSoup
import uuid

async def fetch(url,expectedResponse):
    async def fetchResponse():
        async with async_playwright() as session:
            browser = await session.chromium.launch()
            page = await browser.new_page()
            async with page.expect_response(lambda response: expectedResponse in response.url) as resp:
                await page.goto(url)
            resp_value = await resp.value
            json = await resp_value.json()
            await page.close()
            return json
    
    mytask = asyncio.create_task(fetchResponse())

    return await asyncio.wait_for(mytask,timeout=10)

async def downloadAllImages(url):
    async def handle(response):
        with open(f'{uuid.uuid4()}.png','wb') as f:
            f.write(response.body)

    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        await page.route('**/*.{png,jpg,jpeg}', handle)
        await page.wait_for_timeout(1000*10)

async def getPageContentIntoBsp(url):
    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        soup = BeautifulSoup(page.content(), 'html.parser')
        return soup


async def main():
    # Go to mercari japan Pikachu ピカチュウ and intercept the response!
    url = "https://jp.mercari.com/search?keyword=ピカチュウ"
    intercept = 'https://api.mercari.jp/v2/entities:search'
    data = await fetch(url,intercept)
    print(data)    

    await downloadAllImages(url)

    parsedBsp = await getPageContentIntoBsp()
    print(parsedBsp)

asyncio.run(main())