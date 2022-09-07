from api.user_data.storage.db_connect import get_session

CREATE_API_CACHE_TABLE_CQL = '''
CREATE TABLE IF NOT EXISTS model_serving_api_cache (
    endpoint    TEXT,
    version     TEXT,
    input_json  TEXT,
    output_json TEXT,
    PRIMARY KEY (( endpoint, version, input_json ))
);
'''

CREATE_API_CALL_LOG_CQL = '''
CREATE TABLE IF NOT EXISTS spam_calls_log (
    caller_id   TEXT,
    version     TEXT,
    called_at   TIMESTAMP,
    endpoint    TEXT,
    input_json  TEXT,
    PRIMARY KEY (( caller_id, version ), called_at )
) WITH default_time_to_live = 3600;
'''


if __name__ == '__main__':
    # get db connection
    session = get_session()
    # create table (Note: handling schema changes programmatically
    # is usually a bad idea in production ...)
    session.execute(CREATE_API_CACHE_TABLE_CQL)
    session.execute(CREATE_API_CALL_LOG_CQL)
    print('Tables created (if needed).')
