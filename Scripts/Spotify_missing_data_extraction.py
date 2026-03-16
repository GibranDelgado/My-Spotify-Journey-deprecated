import pandas as pd
import json
import Scripts.Spotify_utilities as Utilities
import Scripts.Spotify_methods as Methods


class PlaylistTracksMatcher:
    def __init__(self, token, playlists_file):
        self.token = token
        self.playlists_file = playlists_file

    def _open_json_file(self, file):
        with open(file, encoding="utf-8") as json_file:
            return json.load(json_file)["playlists"]

    def _load_playlists(self):
        raw_playlists = self._open_json_file(self.playlists_file)
        playlists = [r["items"] for r in raw_playlists]

        tracks_appended = pd.DataFrame(
            [
                tracks["track"]
                for playlist in playlists
                for tracks in playlist
                if "track" in tracks.keys()
            ]
        ).assign(
            trackID=lambda df: df["trackUri"].str.replace("spotify:track:", "")
        )

        return tracks_appended.loc[:, ["trackID", "artistName", "trackName"]]

    def process(self, SH):
        cols = ["artistName", "trackName"]

        uq_artist_tracks = SH[cols].drop_duplicates().reset_index(drop=True)
        playlists_info = self._load_playlists()

        found, not_found = Methods.MatcherResults().match_dfs(
            uq_artist_tracks, playlists_info
        )
        
        found = (
            Methods.ComplementaryInfoExtractor(self.token, found)
            .collecting_info("tracks")
            .drop(columns=["duration", "explicit"])
        )

        return found, not_found


class TrackCountSplitter:
    def split(self, df, threshold):
        cols = ["artistName", "trackName"]

        uq_artist_tracks = df[cols].drop_duplicates()

        tracks_count = (
            uq_artist_tracks.groupby("artistName")
            .agg("count")
            .reset_index()
            .rename(columns={"trackName": "tracksNumber"})
        )

        results = pd.merge(
            uq_artist_tracks, tracks_count, how="inner", on="artistName"
        )

        mask = results["tracksNumber"] < threshold

        few = results.loc[mask, cols].reset_index(drop=True)
        many = results.loc[~mask, cols].reset_index(drop=True)

        return few, many


class ArtistTracksFinder:
    def __init__(self, token):
        self.token = token
        self.match_accumulator = Methods.ResultsAccumulator()

    def process(self, df):
        for artist in pd.unique(df["artistName"]):
            print(f"\nSearching {artist} tracks...")

            pending = df[df["artistName"] == artist]

            results = Methods.SearchingItems(self.token).search(
                used_class=Utilities.SearchSampleArtistTracks, item=artist
            )
            
            candidates = Methods.ExtractTracksInfo().results_to_df(results)
            found, not_found = Methods.MatcherResults().match_dfs(
                pending, candidates
            )

            if not found.empty:
                print(f"\n{found.shape[0]} tracks found!")
                self.match_accumulator.add_results(found)

                pending = not_found
                print(f"{pending.shape[0]} tracks left")

    def final_results(self):
        cols = ["artistName", "trackName"]
        return self.match_accumulator.final_results(cols)


class MultipleTracksFinder:
    def __init__(self, token):
        self.token = token
        self.match_accumulator = Methods.ResultsAccumulator()

    def process(self, df):
        for row in df.itertuples(index=True):
            num_tracks = df.shape[0]
            i, artist, track = row[0], row[1], row[2]

            print(f"\nSearching the track: {track} ({i+1} of {num_tracks})")

            
            results = Methods.SearchingItems(self.token).search(
                used_class=Utilities.SearchTracks, item=track
            )

            for result in results:
                candidates = Methods.ExtractTracksInfo().results_to_df(result)
                found = Methods.MatcherResults().match_single_value(
                    candidates, artist, track
                )

                if not found.empty:
                    print("Track found!")
                    self.match_accumulator.add_results(found)
                    break

    def final_results(self):
        cols = ["artistName", "trackName"]
        return self.match_accumulator.final_results(cols)