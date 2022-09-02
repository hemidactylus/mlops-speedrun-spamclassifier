import os
import sys
import pandas as pd
from time_uuid import TimeUUID
from datetime import datetime

from feast import FeatureStore
from feast.data_source import PushMode

from api.user_data.storage.db_connect import get_session
from analysis.features2.feature2_extractor import Feature2Extractor

base_dir = os.path.abspath(os.path.dirname(__file__))
store_dir = os.path.join(base_dir, '..', 'sms_feature_store')

if __name__ == '__main__':
    #
    push_mode = PushMode.ONLINE_AND_OFFLINE
    push_source_name = 'smss2_push'
    #
    store = FeatureStore(repo_path=store_dir)
    db_session = get_session()
    user_ids = sys.argv[1:]
    feature2_extractor = Feature2Extractor()
    #
    print('** Backfilling v2-features (for model v3) to feature store')
    print(f'** Target user_id = {" ".join(user_ids)}')
    #
    retrieve_smss_cql = db_session.prepare('SELECT * FROM smss_by_users WHERE user_id=?;')
    for user_id in user_ids:
        print(f'    - user_id "{user_id}" ... ', end='')
        rows = list(db_session.execute(
            retrieve_smss_cql,
            (user_id, ),
        ))
        print(f'{len(rows)} items found. ', end='')
        insertion_df = pd.DataFrame.from_dict({
            'sms_id': [
                str(row.sms_id)
                for row in rows
            ],
            'event_timestamp': [
                datetime.fromtimestamp(TimeUUID(bytes=row.sms_id.bytes).get_timestamp())
                for row in rows
            ],
            'features': [
                feature2_extractor.get_features_list(row.sms_text)
                for row in rows
            ],
        })
        #
        print('Store-insert ... ', end='')
        store.push(
            push_source_name=push_source_name,
            df=insertion_df,
            to=push_mode,
        )
        print('done.')
        #
        print(f'      sms_ids: {" ".join(sorted(str(row.sms_id) for row in rows))}')
    print('Backfill completed.')
