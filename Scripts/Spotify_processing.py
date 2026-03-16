import os
import time
import pandas as pd
from Scripts.Spotify_methods import MatcherResults, ComplementaryInfoExtractor
from . import Spotify_missing_data_extraction as SMDE


class SpotifyPipeline:
    def __init__(self, token_gen, SH, playlists_file):
        self.token_gen = token_gen
        self.SH = SH
        self.playlists_file = playlists_file

    def extract_from_playlists(self):
        token = self.token_gen.get()
        return SMDE.PlaylistTracksMatcher(token, self.playlists_file).process(
            self.SH
        )

    def _exec_strategy(self, method, df):
        start = time.time()

        token = self.token_gen.get()

        finder = method(token)
        finder.process(df)
        results = finder.final_results()

        end = time.time()

        found, miss = MatcherResults().match_dfs(df, results)
        
        delay = 120
        time.sleep(delay)

        return {"Found": found, "Miss": miss, "Time": end - start}

    def _define_match_pipeline(self, few, many):
        return (
            self._exec_strategy(SMDE.ArtistTracksFinder, few),
            self._exec_strategy(SMDE.MultipleTracksFinder, many),
        )

    def run_match_pipeline(self, df):
        few, many = SMDE.TrackCountSplitter().split(df, threshold=5)
        results_1 = list(self._define_match_pipeline(few, many))

        miss_few = results_1[0]["Miss"]
        miss_many = results_1[1]["Miss"]
        results_2 = list(self._define_match_pipeline(miss_many, miss_few))

        all_results = results_1 + results_2

        succ_info = pd.concat([r["Found"] for r in all_results])
        miss_info = pd.concat([r["Miss"] for r in results_2])
        exec_time = sum([r["Time"] for r in all_results])

        return succ_info, miss_info, exec_time


class OutputGenerator:
    def __init__(self, token_gen, SH, succ_info, output_path):
        self.token_gen = token_gen
        self.SH = SH
        self.succ_info = succ_info
        self.output_path = output_path
        self.cols = ["artistName", "trackName"]

    def _update_sh(self):
        return pd.merge(self.SH, self.succ_info, how="inner", on=self.cols)

    def _df_to_excel(self, df, file_name):
        path = os.path.join(self.output_path, f"{file_name}.xlsx")
        df.to_excel(path, index=False)

    def export_files(self):
        token = self.token_gen.get()
        sh_complete = self._update_sh()

        comp_info = ComplementaryInfoExtractor(token, self.succ_info)

        tracks_info = comp_info.collecting_info("tracks")
        albums_info = comp_info.collecting_info("albums")
        artists_info = comp_info.collecting_info("artists")

        self._df_to_excel(sh_complete, "streaming_history")
        self._df_to_excel(tracks_info, "tracks")
        self._df_to_excel(albums_info, "albums")
        self._df_to_excel(artists_info, "artists")
