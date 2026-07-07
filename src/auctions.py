"""
auctions.py

Reconstruct one row per auction from the raw event log.

Author: Mathieu Scott
"""

import duckdb


def build_auction_table(file_path: str):
    """
    Builds an auction-level table from the raw event log.

    Returns a Pandas DataFrame where each row represents
    one auction and its lifecycle.
    """

    con = duckdb.connect()

    query = f"""
    SELECT

        auction_id,

        MIN(prt_dt) AS event_date,

        MIN(CASE WHEN event='Start' THEN CAST(time_stamp AS BIGINT) END) AS start_ts,

        MAX(CASE WHEN event='Complete' THEN CAST(time_stamp AS BIGINT) END) AS complete_ts,

        COUNT(*) AS event_count,

        ANY_VALUE(publisher_id) AS publisher_id,

        ANY_VALUE(exchange_id) AS exchange_id,

        ANY_VALUE(deal_id) AS deal_id,

        ANY_VALUE(dsp_device_type) AS dsp_device_type,

        ANY_VALUE(p39_device_type) AS p39_device_type,

        ANY_VALUE(appstore_app_name) AS app_name,

        ANY_VALUE(ctv_store_name) AS store,

        ANY_VALUE(geo_as_0) AS asn,

        ANY_VALUE(datacenter) AS datacenter,

        ANY_VALUE(household) AS household,

        ANY_VALUE(wireless) AS wireless

    FROM '{file_path}'

    GROUP BY auction_id
    """

    auctions = con.sql(query).df()

    auctions["has_start"] = auctions["start_ts"].notna()

    auctions["has_complete"] = auctions["complete_ts"].notna()

    auctions["duration_sec"] = (
        auctions["complete_ts"] - auctions["start_ts"]
    )

    return auctions