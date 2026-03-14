# My Spotify Journey
Thank you for your interest in my project. This time I decided to emulate the famous annual Spotify Wrapped, with additional information layers to make an in-depth analysis of my streaming history and create a customized dashboard of my musical preferences, with the advantage of using data from anytime of the year.

## Overview
The streaming history file given by Spotify was used as the data source; however, due only the trackname, the artistname and the endtime of each play and was described in this file, I took the decision to create and end-to-end Python data extraction pipeline using the Spotify Web API, in order to get some useful information to complement the streaming history.

## Content

### Main

### Input_files folder
Three files are required: config.json, Playlist1.json y StreamingHistory_music_0.json. The first one contains the credentials of the project while the last two come from the data that Spotify shares with you when you request for your streaming history (we will talk about this later).

### Scripts folder
This folder acts as a module. Contains the scripts listed below.

- **SpotifyAPI_access**
Includes the function `get_token()` which generates an access token using the `client_secret` and the `client_id` coming from the config.json file

- **Spotify_streaming_history**
Cleans the streaming history updating the playback datetime to the timezone defined in the config.json file

- **Spotify_utilities**
Includes a set of clases used to retrieve information about a track, album or an artist. Use GetTrack, GetAlbum or GetArtist if you already have the corresponding id, in other case, use SearchSampleArtistTracks or SearchTracks if you want to make the search using the artistname or the trackname, respectively.

- **Spotify_methods**
Methods responsible for processing and handling the results from the Spotify API, such as searching tracks, converting them to dataframe, matching the tracks to search against API call results, etc, are defined in this section.

- **Spotify_missing_data_extraction**



