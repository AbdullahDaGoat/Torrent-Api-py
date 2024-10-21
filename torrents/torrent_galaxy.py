import time
import aiohttp
from bs4 import BeautifulSoup
from helper.html_scraper import Scraper
from constants.base_url import TGX

class TorrentGalaxy:
    def __init__(self):
        self.BASE_URL = TGX
        self.LIMIT = None

    def _parser_individual(self, html):
        try:
            soup = BeautifulSoup(html[0], "html.parser")
            my_dict = {"data": []}
            root_div = soup.find("div", class_="gluewrapper")
            post_nd_torrents = root_div.find_next("div").find_all("div")
            torrentsand_all = post_nd_torrents[4].find_all("a")
            magnet_link = torrentsand_all[1]["href"]

            details_root = soup.find("div", class_="gluewrapper").select(
                "div > :nth-child(2) > div > .tprow"
            )

            name = details_root[0].find_all("div")[-1].get_text(strip=True)

            my_dict["data"].append(
                {
                    "name": name,
                    "magnet": magnet_link,
                }
            )
            return my_dict
        except:
            return None

    def _parser(self, htmls):
        try:
            for html in htmls:
                soup = BeautifulSoup(html, "html.parser")

                my_dict = {"data": []}
                for idx, divs in enumerate(soup.find_all("div", class_="tgxtablerow")):
                    div = divs.find_all("div")
                    try:
                        name = div[4].find("a").get_text(strip=True)
                    except:
                        name = (div[1].find("a", class_="txlight")).find("b").text

                    if name != "":
                        try:
                            magnet = div[5].find_all("a")[1]["href"]
                        except:
                            magnet = div[3].find_all("a")[1]["href"]

                        my_dict["data"].append(
                            {
                                "name": name,
                                "magnet": magnet,
                            }
                        )
                    if len(my_dict["data"]) == self.LIMIT:
                        break
                try:
                    ul = soup.find_all("ul", class_="pagination")[-1]
                    tpages = ul.find_all("li")[-2]
                    my_dict["current_page"] = int(
                        soup.select_one("li.page-item.active.txlight a").text.split(
                            " "
                        )[0]
                    )
                    my_dict["total_pages"] = int(tpages.find("a").text)
                except:
                    my_dict["current_page"] = None
                    my_dict["total_pages"] = None
                return my_dict
        except:
            return None

    async def search(self, query, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            url = (
                self.BASE_URL
                + "/torrents.php?search=+{}&sort=seeders&order=desc&page={}".format(
                    query, page - 1
                )
            )
            return await self.parser_result(start_time, url, session)

    async def get_torrent_by_url(self, torrent_url):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            return await self.parser_result(
                start_time, torrent_url, session, is_individual=True
            )

    async def parser_result(self, start_time, url, session, is_individual=False):
        html = await Scraper().get_all_results(session, url)
        if is_individual:
            results = self._parser_individual(html)
        else:
            results = self._parser(html)
        if results is not None:
            results["time"] = time.time() - start_time
            results["total"] = len(results["data"])
            return results
        return results

    async def trending(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            url = self.BASE_URL
            return await self.parser_result(start_time, url, session)

    async def recent(self, category, page, limit):
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            self.LIMIT = limit
            if not category:
                url = self.BASE_URL + "/latest"
            else:
                if category == "documentaries":
                    category = "Docus"
                url = (
                    self.BASE_URL
                    + "/torrents.php?parent_cat={}&sort=id&order=desc&page={}".format(
                        str(category).capitalize(), page - 1
                    )
                )
            return await self.parser_result(start_time, url, session)
