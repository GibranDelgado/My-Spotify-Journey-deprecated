import pandas as pd
import time
from unidecode import unidecode
from . import Spotify_utilities as Utilities


class SearchingItems:
    def __init__(self, token):
        self.token = token

    def search(self, used_class, item):
        offset = 0
        limit = 10
        delay = 5

        try:
            results = used_class(
                self.token, item, offset, limit, clean=False
            ).access_to_results()

        except KeyError:
            results = used_class(
                self.token, item, offset, limit, clean=True
            ).access_to_results()

        time.sleep(delay)

        return results


class ExtractTracksInfo:
    def _results_to_dict(self, results):
        return {
            "artistName": results["artists"][0]["name"],
            "trackName": results["name"],
            "albumName": results["album"]["name"],
            "trackID": results["id"],
            "artistID": results["artists"][0]["id"],
            "albumID": results["album"]["id"],
        }

    def results_to_df(self, results):
        return pd.DataFrame([self._results_to_dict(r) for r in results])


class MatcherResults:
    def __init__(self):
        self.cols = ["artistName", "trackName"]

    def _norm_col(self, df, col):
        return df[col].str.lower().apply(unidecode)

    def _norm_str(self, item):
        return unidecode(item.lower())

    def _update_df(self, df):
        return df.assign(
            artistName_lower=self._norm_col(df, "artistName"),
            trackName_lower=self._norm_col(df, "trackName"),
        )

    def match_dfs(self, pending, candidates):
        pending = self._update_df(pending)
        candidates = self._update_df(candidates).drop(columns=self.cols)

        new_cols = ["artistName_lower", "trackName_lower"]

        results = pd.merge(
            pending, candidates, how="left", on=new_cols, indicator=True
        ).drop(columns=new_cols)

        mask = results["_merge"] == "both"

        found = results[mask].drop(columns="_merge")
        not_found = results.loc[~mask, self.cols]

        return found, not_found

    def match_single_value(self, candidates, artist, track):
        return candidates[
            (self._norm_col(candidates, "artistName") == self._norm_str(artist))
            & (self._norm_col(candidates, "trackName") == self._norm_str(track))
        ]


class ResultsAccumulator:
    def __init__(self):
        self.matches = []

    def add_results(self, df):
        self.matches.append(df)

    def final_results(self, cols):
        return (
            pd.concat(self.matches).groupby(cols).first().reset_index()
            if self.matches
            else pd.DataFrame(None)
        )


class ComplementaryInfoExtractor:
    def __init__(self, token, succ_info):
        self.token = token
        self.succ_info = succ_info

    def _map_tracks(self, result):
        return {
            "artistName": result["artists"][0]["name"],
            "trackName": result["name"],
            "albumName": result["album"]["name"],
            "trackID": result["id"],
            "artistID": result["artists"][0]["id"],
            "albumID": result["album"]["id"],
            "duration": result["duration_ms"],
            "explicit": result["explicit"],
        }

    def _map_albums(self, result):
        return {
            "albumName": result["name"],
            "albumID": result["id"],
            "artistName": result["artists"][0]["name"],
            "artistID": result["artists"][0]["id"],
            "release_date": result["release_date"][:4],
            "album_type": result["album_type"],
            "label": result["label"],
            "total_tracks": result["total_tracks"],
        }

    def _map_artists(self, result):
        return {
            "artistName": result["name"],
            "artistID": result["id"],
            "genres": result["genres"],
        }

    def collecting_info(self, datatype):
        params = {
            "tracks": ["trackID", Utilities.GetTrack, self._map_tracks],
            "albums": ["albumID", Utilities.GetAlbum, self._map_albums],
            "artists": ["artistID", Utilities.GetArtist, self._map_artists],
        }

        col_name, utility_class, map_class = params[datatype]
        ids = pd.unique(self.succ_info[col_name])

        results = []
        delay = 2.5

        print(f"\nGetting complementary info ({datatype})")

        for i, item_id in enumerate(ids):
            print(f"{datatype[:-1]} {i} of {len(ids)}")

            result = utility_class(
                token=self.token, item_id=item_id
            ).access_to_results()

            time.sleep(delay)

            if result:
                results.append(map_class(result))

        results = pd.DataFrame(results)

        if datatype == "artists":
            results = results.explode("genres")
            results.loc[results["genres"].isna(), "genres"] = "unknown"

        return results