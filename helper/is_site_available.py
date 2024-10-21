from torrents.kickass import Kickass
from torrents.limetorrents import Limetorrent
from torrents.pirate_bay import PirateBay
from torrents.torlock import Torlock
from torrents.torrent_galaxy import TorrentGalaxy
from torrents.yts import Yts

def check_if_site_available(site):
    all_sites = {
        "torlock": {
            "website": Torlock,
            "trending_available": True,
            "trending_category": True,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": True,
            "categories": [
                "anime",
                "music",
                "games",
                "tv",
                "apps",
                "documentaries",
                "other",
                "xxx",
                "movies",
                "books",
                "images",
            ],
            "limit": 50,
        },
        "tgx": {
            "website": TorrentGalaxy,
            "trending_available": True,
            "trending_category": True,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": True,
            "categories": [
                "anime",
                "music",
                "games",
                "tv",
                "apps",
                "documentaries",
                "other",
                "xxx",
                "movies",
                "books",
            ],
            "limit": 50,
        },
        "piratebay": {
            "website": PirateBay,
            "trending_available": True,
            "trending_category": False,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": True,
            "categories": ["tv"],
            "limit": 50,
        },
        "kickass": {
            "website": Kickass,
            "trending_available": True,
            "trending_category": True,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": True,
            "categories": [
                "anime",
                "music",
                "games",
                "tv",
                "apps",
                "documentaries",
                "other",
                "xxx",
                "movies",
                "books",
            ],
            "limit": 50,
        },
        "yts": {
            "website": Yts,
            "trending_available": True,
            "trending_category": False,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": False,
            "categories": [],
            "limit": 20,
        },
        "limetorrent": {
            "website": Limetorrent,
            "trending_available": True,
            "trending_category": False,
            "search_by_category": False,
            "recent_available": True,
            "recent_category_available": True,
            "categories": [
                "anime",
                "music",
                "games",
                "tv",
                "apps",
                "other",
                "movies",
                "books",
            ],
            "limit": 50,
        },
    }

    if site in all_sites.keys():
        return all_sites
    return False
