import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from helper.asyncioPoliciesFix import decorator_asyncio_fix
from helper.html_scraper import Scraper
from constants.base_url import TORLOCK
from constants.headers import HEADER_AIO

class Torlock:
    def __init__(self):
        self.BASE_URL = TORLOCK
        self.LIMIT = None

    @decorator_asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                try:
                    tm = soup.find_all("a")
                    magnet = tm[20]["href"]
                    if str(magnet).startswith("magnet"):
                        obj["magnet"] = magnet
                    else:
                        del obj
                except IndexError:
                    ...
        except:
            return None

    async def _get_torrent(self, result, session, urls):
        tasks = []
        for idx, url in enumerate(urls):
            for obj in result["data"]:
                if obj["url"] == url:
                    task = asyncio.create_task(
                        self._individual_scrap(session, url, result["data"][idx])
                    )
                    tasks.append(task)
        await asyncio.gather(*tasks)
        return result

    def _parser(self, htmls, idx=0):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}

                for tr in soup.find_all("tr")[idx:]:
                    td = tr.find_all("td")
                    if len(td) == 0:
                        continue
                    name = td[0].get_text(strip=True)
                    if name != "":
                        url = td[0].find("a")["href"]
                        if url == "":
                            break
                        url = self.BASE_URL + url
                        list_of_urls.append(url)
                        my_dict["data"].append(
                            {
                                "name": name,
                                "url": url,
                            }
                        )
                    if len(my_dict["data"]) == self.LIMIT:
                        break
                try:
                    ul = soup.find("ul", class_="pagination")
                    tpages = ul.find_all("a")[-2].text
                    current_page = (
                        (ul.find("li", class_="active")).find("span").text.split(" ")[0]
                    )
                    my_dict["current_page"] = int(current_page)
                    my_dict["total_pages"] = int(tpages)
                except:
                    my_dict["current_page"] = None
                    my_dict["total_pages"] = None
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            url = self.BASE_URL + "/all/torrents/{}.html?sort=seeds&page={}".format(
                query, page
            )
            return await self.parser_result(start_time, url, session, idx=5)

    async def parser_result(self, start_time, url, session, idx=0):
        htmls = await Scraper().get_all_results(session, url)
        result, urls = self._parser(htmls, idx)
        if result is not None:
            results = await self._get_torrent(result, session, urls)
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return result

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            if not category:
                url = self.BASE_URL
            else:
                if category == "books":
                    category = "ebooks"
                url = self.BASE_URL + "/{}.html".format(category)
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            if not category:
                url = self.BASE_URL + "/fresh.html"
            else:
                if category == "books":
                    category = "ebooks"
                url = self.BASE_URL + "/{}/{}/added/desc.html".format(category, page)
            return await self.parser_result(start_time, url, session)
