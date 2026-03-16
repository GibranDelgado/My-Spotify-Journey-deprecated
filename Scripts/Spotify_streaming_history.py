import json
import pandas as pd
from zoneinfo import ZoneInfo


class StreamingHistory:
    def __init__(self, config_file, sh_file):
        self.config_file = config_file
        self.sh_file = sh_file

    def _open_json_file(self, file):
        with open(file, encoding="utf-8") as json_file:
            return json.load(json_file)

    def _time_zone_converter(self, SH):
        config_vars = self._open_json_file(self.config_file)
        time_zone = config_vars["time_zone"]

        return pd.to_datetime(SH["endTime"], utc=True).dt.tz_convert(
            ZoneInfo(time_zone)
        )

    def load(self):
        SH = pd.DataFrame(self._open_json_file(self.sh_file))
        SH["startTime"] = self._time_zone_converter(SH) - pd.to_timedelta(
            SH["msPlayed"], unit="ms"
        )

        return SH.loc[:, ["startTime", "artistName", "trackName", "msPlayed"]]