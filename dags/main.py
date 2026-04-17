from airflow import DAG
import pendulum
from datetime import datetime ,timedelta
from api.video_stats import (
    get_playlist_id,
    get_video_ids,
    extract_video_data,
    save_to_json,
)

from datawarehoues.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

local_tz = pendulum.timezone("Asia/Bangkok")

default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "dataengineers@example.com",
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2026, 4, 17, tzinfo=local_tz),
    # "end_date": datetime(2026, 4, 30, tzinfo=local_tz)
}


# Variables
staging_schema = "staging"
core_schema = "core"


with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="A DAG to extract video data from YouTube API and save it as JSON",
    schedule='0 14 * * *',  # Run every day at 14:00 ICT (UTC+7)
    catchup=False
)as dag:

    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)

with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON files and update the staging and core schemas",
    schedule='0 15 * * *',  # Run every day at 15:00 ICT (UTC+7)
    catchup=False
)as dag:

    update_staging = staging_table()
    update_core = core_table()

    update_staging >> update_core


with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="DAG to check the data quality on both layers in the database",
    catchup=False,
    schedule='0 16 * * *',  # Run every day at 16:00 ICT (UTC+7)
) as dag_quality:

    # Define tasks
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Define dependencies
    soda_validate_staging >> soda_validate_core