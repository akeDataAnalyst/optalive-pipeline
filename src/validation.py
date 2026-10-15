import pandas as pd
import numpy as np

class OptaLiveValidator:
    """
    Automated Quality Assurance engine for live sports event collection.
    Evaluates starting lineups, event completeness, card classifications,
    and substitution pairing.
    """

    def __init__(self, key_events_df, lineup_df):
        self.events = key_events_df.copy() if not key_events_df.empty else pd.DataFrame()
        self.lineup = lineup_df.copy() if not lineup_df.empty else pd.DataFrame()

    def validate_events(self):
        """
        Applies data quality rules across all key match events.
        Returns a DataFrame enriched with 'validation_status' and 'issue_description'.
        """
        if self.events.empty:
            return pd.DataFrame()

        validated_records = []
        player_yellow_cards = {}  # Tracks yellow card counts per player for escalation checks

        for idx, row in self.events.iterrows():
            status = "Valid"
            issues = []

            event_id = row.get("event_id")
            event_type = row.get("event_type")
            period = row.get("period")
            minute = row.get("minute")
            second = row.get("second")
            team_name = row.get("team_name")
            player_name = row.get("player_name")
            player_id = row.get("player_id")
            card_class = row.get("card_classification")
            sub_in = row.get("sub_player_in")

            # Rule 1: Check required timestamp fields
            if pd.isna(minute) or pd.isna(period):
                status = "Error"
                issues.append("Missing minute or period timestamp.")
            elif minute < 0 or minute > 130:
                status = "Error"
                issues.append(f"Invalid match minute recorded: {minute}.")

            # Rule 2: Goal validation (Must have player and team)
            if event_type == "Goal":
                if pd.isna(player_name) or pd.isna(team_name):
                    status = "Error"
                    issues.append("Goal event missing scoring player or team attribution.")

            # Rule 3: Card classification and state tracking
            if event_type == "Card":
                if pd.isna(player_name):
                    status = "Error"
                    issues.append("Card event missing player attribution.")
                
                if pd.isna(card_class):
                    status = "Warning"
                    issues.append("Unclassified card type recorded.")
                elif card_class == "Yellow Card":
                    player_yellow_cards[player_id] = player_yellow_cards.get(player_id, 0) + 1
                    if player_yellow_cards[player_id] > 1:
                        status = "Warning"
                        issues.append(f"Player received second yellow card without 'Second Yellow' event flag.")
                elif card_class == "Second Yellow":
                    player_yellow_cards[player_id] = player_yellow_cards.get(player_id, 0) + 1

            # Rule 4: Substitution validation (Must have both outgoing and incoming players)
            if event_type == "Substitution":
                if pd.isna(player_name) or pd.isna(sub_in):
                    status = "Error"
                    issues.append("Substitution incomplete: missing outgoing or incoming player.")

            # Rule 5: Starting XI validation
            if event_type == "Starting XI":
                if pd.isna(team_name):
                    status = "Error"
                    issues.append("Starting XI submission missing team identifier.")

            issue_str = " | ".join(issues) if issues else "No issues detected."

            record = row.to_dict()
            record["validation_status"] = status
            record["issue_description"] = issue_str
            validated_records.append(record)

        return pd.DataFrame(validated_records)

    def generate_data_quality_report(self):
        """
        Calculates match-level data quality metrics and an overall health score (0-100%).
        """
        df_validated = self.validate_events()
        if df_validated.empty:
            return {
                "total_events": 0,
                "valid_events": 0,
                "warnings": 0,
                "errors": 0,
                "quality_score": 0.0
            }

        total = len(df_validated)
        valid_count = (df_validated["validation_status"] == "Valid").sum()
        warning_count = (df_validated["validation_status"] == "Warning").sum()
        error_count = (df_validated["validation_status"] == "Error").sum()

        # Quality Score Formula: Start at 100%, deduct 10% per error, 3% per warning
        deductions = (error_count * 10.0) + (warning_count * 3.0)
        quality_score = max(0.0, min(100.0, 100.0 - (deductions / max(1, total) * 100)))

        return {
            "total_events": total,
            "valid_events": valid_count,
            "warnings": warning_count,
            "errors": error_count,
            "quality_score": round(quality_score, 2)
        }