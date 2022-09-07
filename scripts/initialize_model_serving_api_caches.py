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


if __name__ == '__main__':
    # get db connection
    session = get_session()
    # create table (Note: handling schema changes programmatically
    # is usually a bad idea in production ...)
    session.execute(CREATE_API_CACHE_TABLE_CQL)
    print('Table created (if needed).')
