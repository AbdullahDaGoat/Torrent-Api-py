import asyncio
import re
import time
import aiohttp
from bs4 import BeautifulSoup
from helper.asyncioPoliciesFix import decorator_asyncio_fix
from helper.html_scraper import Scraper
from constants.base_url import YTS
from constants.headers import HEADER_AIO

class Yts:
    def __init__(self):
        self.BASE_URL = YTS
        self.LIMIT = None

    @decorator_asyncio_fix
    async def _individual_scrap(self, session, url, obj):
        try:
            async with session.get(url, headers=HEADER_AIO) as res:
                html = await res.text(encoding="ISO-8859-1")
                soup = BeautifulSoup(html, "html.parser")
                try:
                    name = soup.select_one("div.hidden-xs h1").text
                    torrents = []
                    for div in soup.find_all("div", class_="modal-torrent"):
                        magnet = div.find("a", class_="magnet-download")["href"]
                        torrents.append({"magnet": magnet})
                    obj["name"] = name
                    obj["torrents"] = torrents
                except:
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

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")
                list_of_urls = []
                my_dict = {"data": []}
                for div in soup.find_all("div", class_="browse-movie-wrap"):
                    url = div.find("a")["href"]
                    list_of_urls.append(url)
                    my_dict["data"].append({"url": url})
                    if len(my_dict["data"]) == self.LIMIT:
                        break
                try:
                    ul = soup.find("ul", class_="tsc_pagination")
                    current_page = ul.find("a", class_="current").text
                    my_dict["current_page"] = int(current_page)
                    if current_page:
                        total_results = soup.select_one(
                            "body > div.main-content > div.browse-content > div > h2 > b"
                        ).text
                        if "," in total_results:
                            total_results = total_results.replace(",", "")
                        total_page = int(total_results) / 20
                        my_dict["total_pages"] = (
                            int(total_page) + 1
                            if type(total_page) == float
                            else int(total_page)
                        )
                except:
                    ...
                return my_dict, list_of_urls
        except:
            return None, None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            if page != 1:
                url = (
                    self.BASE_URL
                    + "/browse-movies/{}/all/all/0/latest/0/all?page={}".format(
                        query, page
                    )
                )
            else:
                url = self.BASE_URL + "/browse-movies/{}/all/all/0/latest/0/all".format(
                    query
                )
            return await self.parser_result(start_time, url, session)

    async def parser_result(self, start_time, url, session):
        htmls = await Scraper().get_all_results(session, url)
        result, urls = self._parser(htmls)
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
            url = self.BASE_URL + "/trending-movies"
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            if page != 1:
                url = (
                    self.BASE_URL
                    + "/browse-movies/0/all/all/0/featured/0/all?page={}".format(page)
                )
            else:
                url = self.BASE_URL + "/browse-movies/0/all/all/0/featured/0/all"
            return await self.parser_result(start_time, url, session)
