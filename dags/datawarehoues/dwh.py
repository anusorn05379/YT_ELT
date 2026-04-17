from datawarehoues.data_utils import get_conn_cursor, close_conn_cursor, create_schema, create_table, get_video_ids
from datawarehoues.data_loading import load_data
from datawarehoues.data_modification import insert_rows, update_rows, delete_rows
from datawarehoues.data_transformation import transform_data


import logging 
from airflow.decorators import  task

logger = logging.getLogger(__name__)
table = "yt_api"

@task
def staging_table():

    schema = 'staging'

    conn, cur = None, None
    try:
        conn, cur = get_conn_cursor()

        YT_data = load_data()
        logger.info(f"Loaded {len(YT_data)} rows from JSON file")
        create_schema(schema)
        create_table(schema)

        table_ids = get_video_ids(cur, schema)
        logger.info(f"Found {len(table_ids)} existing rows in {schema} table")

        inserted_count = 0
        updated_count = 0

        for row in YT_data:

            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, row)
                inserted_count += 1

            else:
                if row['video_id'] in table_ids:
                    update_rows(cur, conn, schema, row)
                    updated_count += 1
                else:
                    insert_rows(cur, conn, schema, row)
                    inserted_count += 1
        ids_in_json = {row['video_id'] for row in YT_data}

        ids_to_delete = set(table_ids) - ids_in_json

        deleted_count = 0
        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)
            deleted_count = len(ids_to_delete)
        logger.info(f'{schema} table: {inserted_count} inserted, {updated_count} updated, {deleted_count} deleted')
        logger.info(f'{schema} table updated successfully.')
    except Exception as e:
        logger.error(f"Error in {schema} table update: {e}")
        raise e
    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)


@task
def core_table():

    schema = "core"

    conn, cur = None, None

    try:
        conn , cur = get_conn_cursor()

        create_schema(schema)
        create_table(schema)

        table_ids = get_video_ids(cur, schema)
        logger.info(f"Found {len(table_ids)} existing rows in {schema} table")

        current_video_ids = set()

        cur.execute(f"SELECT * FROM staging.{table};")
        rows = cur.fetchall()
        logger.info(f"Loaded {len(rows)} rows from staging table for transformation")

        inserted_count = 0
        updated_count = 0

        for row in rows:

            current_video_ids.add(row["Video_ID"])

            if len(table_ids) == 0:
                transformed_row = transform_data(row)
                insert_rows(cur, conn, schema, transformed_row)
                inserted_count += 1

            else:
                transformed_row = transform_data(row)

                if transformed_row['Video_ID'] in table_ids:
                    update_rows(cur, conn, schema, transformed_row)
                    updated_count += 1
                else:
                    insert_rows(cur, conn, schema, transformed_row)
                    inserted_count += 1

        ids_to_delete = set(table_ids) - current_video_ids

        deleted_count = 0
        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)
            deleted_count = len(ids_to_delete)
        logger.info(f'{schema} table: {inserted_count} inserted, {updated_count} updated, {deleted_count} deleted')
        logger.info(f'{schema} table updated successfully.')
    except Exception as e:
        logger.error(f"An error occurred during the update of the {schema} table: {e}")
        raise e

    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)