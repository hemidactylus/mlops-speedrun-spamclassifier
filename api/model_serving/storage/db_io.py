"""
These functions wrap CQL queries to store and retrieve specific
kind of items from database tables. These are for direct use by the API code.

This module, crucially, holds a process-wide (lazy) cache of CQL
prepared statements, which are used over and over to optimize the API
performance.
"""

import json


prepared_cache = {}
def get_prepared_statement(session, stmt):
    """
    We hold a cache of prepared statements, one per CQL command.
    New CQL statements are prepared and kept in this cache for subsequent
    usage. The cache key is the statement itself (a choice which works because
    (1) no CQL is built programmatically with variable spaces, etc, and
    (2) parameters, or values, are never part of the statements to prepare).
    """
    if stmt not in prepared_cache:
        print(f'[get_prepared_statement] Preparing statement "{stmt}"')
        prepared_cache[stmt] = session.prepare(stmt)
    return prepared_cache[stmt]


def retrieve_cached_prediction(session, endpoint, version, input):
    try:
        input_json = json.dumps(input)
        get_one_cql = 'SELECT output_json FROM model_serving_api_cache WHERE endpoint=? AND version=? AND input_json=?;'
        prepared_get_one = get_prepared_statement(session, get_one_cql)
        row = session.execute(prepared_get_one, (endpoint, version, input_json)).one()
        if row:
            return json.loads(row.output_json)
        else:
            return row
    except Exception as e:
        print('[retrieve_cached_prediction] Cache-read operation failed. Make sure cache table exists.')
        return None

def store_cached_prediction(session, endpoint, version, input, output):
    """
    Here the input and output are serialized before insertion
    """
    try:
        input_json = json.dumps(input)
        output_json = json.dumps(output)
        insert_cql = 'INSERT INTO model_serving_api_cache (endpoint, version, input_json, output_json) VALUES (?, ?, ?, ?);'
        prepared_insert_cql = get_prepared_statement(session, insert_cql)
        session.execute(prepared_insert_cql, (endpoint, version, input_json, output_json))
        return
    except Exception as e:
        print('[store_cached_prediction] Cache-write operation failed. Make sure cache table exists.')
