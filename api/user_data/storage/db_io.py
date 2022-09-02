"""
These functions wrap CQL queries to store and retrieve specific
kind of items from database tables. These are for direct use by the API code.

This module, crucially, holds a process-wide (lazy) cache of CQL
prepared statements, which are used over and over to optimize the API
performance.
"""

from api.user_data.models.response import SMS, DateRichSMS


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


def retrieve_sms(session, user_id, sms_id):
    get_one_cql = 'SELECT * FROM smss_by_users WHERE user_id=? AND sms_id=?;'
    prepared_get_one = get_prepared_statement(session, get_one_cql)
    row = session.execute(prepared_get_one, (user_id, sms_id)).one()
    if row:
        # see a note in 'models.py' about the enrich-with-date extra step
        return DateRichSMS.from_SMS(SMS(**row._asdict()))
    else:
        return row


def retrieve_smss_by_sms_id(session, user_id):
    get_many_cql = 'SELECT * FROM smss_by_users WHERE user_id=?;'
    prepared_get_many = get_prepared_statement(session, get_many_cql)
    rows = session.execute(prepared_get_many, (user_id,))
    return (
        # see a note in 'models.py' about the enrich-with-date extra step
        DateRichSMS.from_SMS(SMS(**row._asdict()))
        for row in rows
    )


def store_sms(session, user_id, sms_id, sender_id, sms_text):
    insert_cql = 'INSERT INTO smss_by_users (user_id, sms_id, sender_id, sms_text) VALUES (?, ?, ?, ?);'
    prepared_insert_cql = get_prepared_statement(session, insert_cql)
    session.execute(prepared_insert_cql, (user_id, sms_id, sender_id, sms_text))
    return
