import uuid

from api.user_data.storage.db_connect import get_session

CREATE_USER_TABLE_CQL = '''
CREATE TABLE IF NOT EXISTS smss_by_users (
    user_id     TEXT,
    sms_id      INT,
    sms_date    TIMESTAMP,
    sender_id   TEXT,
    sms_text    TEXT,
    PRIMARY KEY (( user_id ), sms_id )
)
    WITH CLUSTERING ORDER BY (sms_id DESC)
;
'''

INSERT_SMS_CQL = '''
INSERT INTO smss_by_users
    (user_id, sms_id, sender_id, sms_text)
VALUES
    (?, ?, ?, ?);
'''


if __name__ == '__main__':
    # get db connection
    session = get_session()
    # create table (Note: handling schema changes programmatically
    # is usually a bad idea in production ...)
    session.execute(CREATE_USER_TABLE_CQL)
    print('Table created (if needed).')
    # now a bunch of sample inserts take place, as per this dummy data:
    # { user_id -> [(sms_id, sender_id, sms_text)] }
    # (don't pay too much attention to this script)
    dummy_data = {
        'fiona': [
            (
                # 2019-06-01
                '32e14000-8400-11e9-aeb7-d19b11ef0c7e',
                'nina',
                'Hey, what\'s up?'
            ),
            (
                # 2019-06-02
                '5d4b0000-84c9-11e9-8ef7-b7830748221b',
                'otto',
                'Did you read my book?'
            ),
            (
                # 2019-06-03
                '87b4c000-8592-11e9-bff6-20a2e9f40feb',
                'pete',
                'You win FREE CASH! Click here!'
            ),
            (
                # 2019-06-04
                'b21e8000-865b-11e9-a307-bb1efd5e4096',
                'otto',
                'Tell me if you read my book!?'
            ),
            (
                # 2019-06-05
                'dc884000-8724-11e9-90f9-878916a9ab9c',
                'nina',
                'Want to hang out tomorrow?'
            ),
            (
                # 2019-06-06
                '06f20000-87ee-11e9-a17e-2346fda4221e',
                'max',
                 'My dog has eaten the documents, sorry'
                ),
        ],
        'max': [
            (
                # 2019-06-03
                '87b4c000-8592-11e9-8a3d-0fda955f4faa',
                'roger',
                'If it does not rain, shall we go running in the park?'
            ),
            (
                # 2019-06-04
                'b21e8000-865b-11e9-ac9d-f6b9f2e02b56',
                'fiona',
                'Please sign the documents I left on your desk'
            ),
            (
                # 2019-06-05
                'dc884000-8724-11e9-88b3-91c00fdefc46',
                'roger',
                'I\'m off to paragliding next week :)'
            ),
            (
                # 2019-06-06
                '06f20000-87ee-11e9-841e-5fa98263a085',
                'pete',
                 'You win FREE CASH! Click here!'
            ),
        ],
    }
    #
    insert_sms_statement = session.prepare(INSERT_SMS_CQL)
    print('Inserting data...')
    for user_id, sms_list in dummy_data.items():
        for sms_id, sender_id, sms_text in sms_list:
            session.execute(
                insert_sms_statement,
                (user_id, uuid.UUID(sms_id), sender_id, sms_text),
            )
            print('  *')
    print('Data inserted.')
