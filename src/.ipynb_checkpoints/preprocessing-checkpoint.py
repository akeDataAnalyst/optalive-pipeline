import pandas as pd
import numpy as np

class OptaLivePreprocessor:
    def __init__(self, raw_events_df, lineup_df):
        self.events = raw_events_df.copy()
        self.lineups = lineup_df.copy()

    def extract_key_events(self):
        """
        Filters raw event data and maps it to Opta-style key match events:
        Goals, Cards (Yellow, Second Yellow, Red), Substitutions, and Starting XIs.
        """
        if self.events.empty or "type.name" not in self.events.columns:
            return pd.DataFrame()

        # Target key event categories
        target_types = ["Shot", "Foul Committed", "Substitution", "Starting XI"]
        filtered = self.events[self.events["type.name"].isin(target_types)].copy()

        processed_records = []
        
        for _, row in filtered.iterrows():
            event_type = row.get("type.name")
            match_id = row.get("match_id")
            event_id = row.get("id")
            period = row.get("period")
            minute = row.get("minute")
            second = row.get("second")
            timestamp = row.get("timestamp")
            team_name = row.get("team.name")
            team_id = row.get("team.id")
            player_name = row.get("player.name")
            player_id = row.get("player.id")
            
            detail = "Normal Play"
            card_classification = None
            sub_player_in = None

            # 1. Shot / Goal Classification
            if event_type == "Shot":
                outcome = row.get("shot.outcome.name")
                if outcome == "Goal":
                    event_type = "Goal"
                    body_part = row.get("shot.body_part.name", "Foot")
                    detail = f"Scored via {body_part if pd.notna(body_part) else 'Foot'}"
                else:
                    continue  # Skip non-goal shots for OptaLive's core key event feed

            # 2. Card / Foul Classification
            elif event_type == "Foul Committed":
                card_info = row.get("foul_committed.card.name")
                if pd.notna(card_info):
                    event_type = "Card"
                    card_classification = card_info  # 'Yellow Card', 'Second Yellow', 'Red Card'
                    detail = f"Disciplinary: {card_info}"
                else:
                    continue  # Skip regular fouls without cards

            # 3. Substitution Classification
            elif event_type == "Substitution":
                sub_replacement = row.get("substitution.replacement.name")
                sub_player_in = sub_replacement
                detail = f"Out: {player_name} | In: {sub_replacement}"

            elif event_type == "Starting XI":
                detail = "Starting Lineup Submitted"

            processed_records.append({
                "match_id": match_id,
                "event_id": event_id,
                "period": period,
                "minute": minute,
                "second": second,
                "timestamp": timestamp,
                "team_id": team_id,
                "team_name": team_name,
                "player_id": player_id,
                "player_name": player_name,
                "event_type": event_type,
                "card_classification": card_classification,
                "sub_player_in": sub_player_in,
                "detail": detail
            })

        df_key_events = pd.DataFrame(processed_records)
        
        if not df_key_events.empty:
            # Chronologically sort by period, minute, and second to simulate live match flow
            df_key_events = df_key_events.sort_values(by=["period", "minute", "second"]).reset_index(drop=True)
            
        return df_key_events

    def validate_pre_match_readiness(self):
        """
        Validates team sheets against professional collection standards:
        Checks squad completeness, missing jersey numbers, and required player attributes.
        """
        if self.lineups.empty:
            return pd.DataFrame()

        readiness_report = []
        grouped = self.lineups.groupby(["match_id", "team_id", "team_name"])
        
        for (match_id, team_id, team_name), group in grouped:
            total_players = len(group)
            missing_jersey = group["jersey_number"].isna().sum()
            missing_name = group["player_name"].isna().sum()
            
            status = "Ready"
            notes = []

            if total_players < 11:
                status = "Not Ready"
                notes.append(f"Squad size is {total_players} (Minimum 11 required)")
            if missing_jersey > 0:
                status = "Needs Review"
                notes.append(f"{missing_jersey} player(s) missing jersey numbers")
            if missing_name > 0:
                status = "Not Ready"
                notes.append(f"{missing_name} player(s) missing names")
            
            if not notes:
                notes.append("Team sheet verified successfully against Opta standards.")

            readiness_report.append({
                "match_id": match_id,
                "team_id": team_id,
                "team_name": team_name,
                "total_squad": total_players,
                "missing_jersey_count": missing_jersey,
                "readiness_status": status,
                "notes": " | ".join(notes)
            })

        return pd.DataFrame(readiness_report)