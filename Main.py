import os
import time
import pandas as pd
from scripts.SpotifyAPI_access import get_token
from scripts.Spotify_streaming_history import StreamingHistory
import scripts.Spotify_processing as Processing
    

class TokenGenerator:
    def __init__(self, config_file):
        self.config_file = config_file
        self.token = None
        self.start = None
        
    def _refresh(self):
        self.token = get_token(self.config_file)
        self.start = time.time()
    
    def get(self):
        if not self.token:
            self._refresh()
            
        elif time.time() - self.start > 3300:
            print("Refreshing token...")
            self._refresh()

        return self.token


if __name__ == "__main__":
    main_path = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(main_path, "Input_files")
    output_path = os.path.join(main_path, "Output_files")
    
    config_file = os.path.join(input_path, "Config.json")
    sh_file = os.path.join(input_path, "StreamingHistory_music_0.json")
    playlists_file = os.path.join(input_path, "Playlist1.json")

    
    SH = StreamingHistory(config_file, sh_file).load()
    token_gen = TokenGenerator(config_file)
    
    Pipeline = Processing.SpotifyPipeline(token_gen, SH, playlists_file)

    succ_playlist, miss_playlist = Pipeline.extract_from_playlists()
    succ, miss, exec_time = Pipeline.run_match_pipeline(miss_playlist)
    
    succ = pd.concat([succ_playlist, succ])

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    Processing.OutputGenerator(token_gen, SH, succ, output_path).export_files()