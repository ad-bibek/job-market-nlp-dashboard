"""
FS-4: Validate ingested postings and flag/exclude records missing required fields.
Implements BR-4 from the BRD: title, description, and posted_date are required
for a record to be included in downstream analysis.
"""
import pandas as pd

REQUIRED_FIELDS = ["title", "description", "posted_date"]


def validate(df: pd.DataFrame):
    """
    Returns (clean_df, validation_log_df).
    A record is excluded if any required field is empty/NaN.
    """
    df = df.copy()
    reasons = []

    for field in REQUIRED_FIELDS:
        df[field] = df[field].fillna("").astype(str).str.strip()

    def get_reason(row):
        missing = [f for f in REQUIRED_FIELDS if row[f] == ""]
        return ", ".join(f"missing_{f}" for f in missing) if missing else ""

    df["_validation_reason"] = df.apply(get_reason, axis=1)

    invalid_mask = df["_validation_reason"] != ""
    validation_log = df.loc[invalid_mask, ["posting_id", "company", "_validation_reason"]].rename(
        columns={"_validation_reason": "reason"}
    )
    clean_df = df.loc[~invalid_mask].drop(columns=["_validation_reason"]).reset_index(drop=True)

    return clean_df, validation_log.reset_index(drop=True)
