import re
from requests import get
from Scripts.SpotifyAPI_access import get_auth_header
from abc import ABC, abstractmethod


class SpotifyRequests(ABC):
    def __init__(self, token):
        self.token = token

    def get_result(self, endpoint, params=None):
        URL = f"https://api.spotify.com/v1/{endpoint}"

        response = get(
            URL, headers={"Authorization": f"Bearer {self.token}"}, params=params
        )
        return response.json()

    @abstractmethod
    def build_endpoint(self):
        pass

    def build_params(self):
        return None

    def access_to_results(self):
        endpoint = self.build_endpoint()
        params = self.build_params()
        result = self.get_result(endpoint, params)
        return self.parse_result(result)

    @abstractmethod
    def parse_result(self, result):
        pass


class SpotifySearchBase(SpotifyRequests):
    def __init__(self, token, query, item, search_type, offset, limit, clean):
        super().__init__(token)
        self.query = query
        self.item = item
        self.search_type = search_type
        self.offset = offset
        self.limit = limit
        self.clean = clean

    @staticmethod
    def _clean_characters(string):
        pattern = (
            r"[^a-zA-Z0-9"  # Only letters and digits
            r"\u4E00-\u9FFF"  # chinese regex
            r"\u3040-\u30FF\u31F0-\u31FF\uFF00-\uFFEF"  # japanese regex
            r"\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF"  # korean regex
            r"\s]"
        )
        return re.sub(pattern, "", string)

    def build_endpoint(self):
        return "search"

    def build_params(self):
        if self.clean:
            self.item = self._clean_characters(self.item)

        return {
            "q": f"{self.query}: {self.item}",
            "type": self.search_type,
            "offset": self.offset,
            "limit": self.limit,
        }

    def parse_result(self, result):
        return result[self.search_type + "s"]["items"]


class SpotifySingleRequest(SpotifyRequests):
    def __init__(self, token, query, item_id):
        super().__init__(token)
        self.query = query
        self.item_id = item_id

    def build_endpoint(self):
        return f"{self.query}/{self.item_id}"

    def parse_result(self, result):
        return result


class SearchSampleArtistTracks(SpotifySearchBase):
    def __init__(self, token, item, offset, limit, clean):
        query = "artist"
        search_type = "track"

        super().__init__(token, query, item, search_type, offset, limit, clean)


class SearchTracks(SpotifySearchBase):
    def __init__(self, token, item, offset, limit, clean):
        query = "track"
        search_type = "track"

        super().__init__(token, query, item, search_type, offset, limit, clean)


class GetTrack(SpotifySingleRequest):
    def __init__(self, token, item_id):
        query = "tracks"
        super().__init__(token, query, item_id)


class GetAlbum(SpotifySingleRequest):
    def __init__(self, token, item_id):
        query = "albums"
        super().__init__(token, query, item_id)


class GetArtist(SpotifySingleRequest):
    def __init__(self, token, item_id):
        query = "artists"
        super().__init__(token, query, item_id)
