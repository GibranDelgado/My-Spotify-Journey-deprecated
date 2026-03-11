# My Spotify Journey (DEPRECATED)

Thank you for your interest in my project. This time I decided to emulate the famous annual Spotify Wrapped, with additional information layers to make an in-depth analysis of my streaming history and create a customized dashboard of my musical preferences, with the advantage of using data from anytime of the year. Unfortunately, due the Web API Changelog occurred in March 2026, data extraction projects like this one are not possible anymore due the stricted rate limit implemented.

## Dashboard
See the links below to visualize my dashboard:

- **NovyPro:** https://project.novypro.com/KmFKle  
- **Tableau Public:** https://public.tableau.com/views/Myspotifyjourney/MySpotifyJourney1?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

## Content
This project is divided in two folders

### Input_files
This folder needs to contain these three JSON files: `config.json`, `Playlist1.json` and `StreamingHistory_music_0.json`. The first one will be filled with your own credentials, while the remaining two files will come from a request to spotify for your streaming history data.

### scripts
This folder works as a module, encapsulating scripts listed below:

- **SpotifyAPI_access.py:**
  Includes a function `get_token()` to generate a token using a `client_secret` and a `client_id`, retrieved from the config.json file and a function `get_auth_header()` that generates an `auth_header` based on a given token.

- **Spotify_utilities:**  
  Defines a series requests to the Spotify API in order to retrieve information about tracks, artists, albums, etc.

- **Spotify_methods:**
  Define a series of general methods 


