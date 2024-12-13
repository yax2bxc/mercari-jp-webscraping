import asyncio 
from playwright.async_api import async_playwright, PlaywrightContextManager, Response
from bs4 import BeautifulSoup
import uuid
import os 
from urllib.parse import urlparse

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
    async def handle(response : Response):
        if response.request.resource_type == "image":
            urlstruct = urlparse(response.url)
            filename = os.path.basename(urlstruct.path)
            print(filename)
            with open(f'./images/{filename}','wb') as f:
                f.write(await response.body())

    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        # await page.route('**/*.{png,jpg,jpeg}', handle)
        page.on("response",handle)
        await page.goto(url)
        await page.wait_for_timeout(1000*10)

async def getPageContentIntoBsp(url):
    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        soup = BeautifulSoup(await page.content(), 'html.parser')
        return soup

async def getFirstResponseMeta(url):
    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        async with page.expect_response(lambda response: True) as response_info:
            response = await response_info.value
            print(response.url)
            print(response.status)
            # print(await response.body())
            print(await response.text())

async def getRequests(url,timeout=10000):
    print("Getting Request")
    requests = []

    def handle(request):
        print(request.url)
        requests.append(request)

    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        page.on("request",handle)
        await page.goto(url)
        await page.wait_for_timeout(timeout)
        return requests
        

async def getResponses(url,timeout=10000):
    requests = []

    def handle(request):
        print(request.url)
        requests.append(request)

    async with async_playwright() as session:
        browser = await session.chromium.launch()
        page = await browser.new_page()
        page.on("response",handle)
        await page.goto(url)
        await page.wait_for_timeout(timeout)
        return requests

async def automateLoginSlickdeals():
    async with async_playwright() as session:
        browser = await session.chromium.launch(headless=False)
        page = await browser.new_page()
        url = "https://slickdeals.net/forums/login.php?action_source=Sign+Up+Button&url=%2F"
        await page.goto(url)
        await page.locator("a[id='accountRegisterLink']").click()
        gmail = "SlimJimmy@gmail.com"
        password = "SecretAgent47"
        await page.get_by_label('email').fill(gmail)
        await page.locator("button[data-role='continueTwoStepReg']").click()
        await page.get_by_label('password').fill(password)
        await page.wait_for_timeout(1000*10)

async def main():
    # Go to mercari japan Pikachu ピカチュウ and intercept the response!
    url = "https://jp.mercari.com/search?keyword=ピカチュウ"
    intercept = 'https://api.mercari.jp/v2/entities:search'
    # data = await fetch(url,intercept)
    # print(data)    

    # await downloadAllImages(url)

    # parsedBsp = await getPageContentIntoBsp(url)
    # print(parsedBsp)

    # requests = await downloadAllImages(url)
    # print(requests)

    await automateLoginSlickdeals()
    # await getFirstResponseMeta(url)

asyncio.run(main())