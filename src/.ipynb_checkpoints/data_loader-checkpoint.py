import os
import json
import pandas as pd

class OptaLiveLoader:
    def __init__(self, raw_data_dir="data/raw"):
        self.raw_dir = raw_data_dir

    def load_matches(self, filename="matches_epl_2015_2016.json"):
        """Loads the matches summary file."""
        filepath = os.path.join(self.raw_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Match file not found at {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            matches = json.load(f)
        return pd.DataFrame(matches)

    def load_lineup(self, match_id):
        """Loads home and away lineups for a given match ID."""
        filepath = os.path.join(self.raw_dir, "lineups", f"{match_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Lineup file not found for match {match_id}")
        with open(filepath, "r", encoding="utf-8") as f:
            lineups = json.load(f)
        
        team_lineups = []
        for team in lineups:
            team_id = team.get("team_id")
            team_name = team.get("team_name")
            for player in team.get("lineup", []):
                player_record = {
                    "match_id": match_id,
                    "team_id": team_id,
                    "team_name": team_name,
                    "player_id": player.get("player_id"),
                    "player_name": player.get("player_name"),
                    "jersey_number": player.get("jersey_number"),
                    "country": player.get("country", {}).get("name"),
                    "cards": player.get("cards", []),
                    "positions": [pos.get("position") for pos in player.get("positions", [])]
                }
                team_lineups.append(player_record)
        return pd.DataFrame(team_lineups)

    def load_events(self, match_id):
        """Loads raw event-stream data for a given match ID."""
        filepath = os.path.join(self.raw_dir, "events", f"{match_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Event file not found for match {match_id}")
        with open(filepath, "r", encoding="utf-8") as f:
            events = json.load(f)
        
        # Flatten basic event metadata using pandas json_normalize
        df_events = pd.json_normalize(events)
        df_events["match_id"] = match_id
        return df_events