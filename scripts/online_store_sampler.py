import math
import sys
import os

from feast import FeatureStore

base_dir = os.path.abspath(os.path.dirname(__file__))
store_dir = os.path.join(base_dir, '..', 'sms_feature_store')


def _isnull(val):
    return val is None or (type(val) is float and math.isnan(val))


def _validate_id(s):
    if s != '':
        return s
    else:
        return None


if __name__ == '__main__':
    #
    if sys.argv[1:] == []:
        sms_ids = ['sms14050', 'sms14051', 'sms14052']
    else:
        sms_ids = sorted({
            _id
            for _id in (
                _validate_id(s_id.strip())
                for c_block in sys.argv[1:]
                for s_id in c_block.split(',')
            )
            if _id is not None
        })
    #
    print(f'** READING FROM ONLINE STORE.\n   SMS IDs = {str(sms_ids)}\n')
    #
    store = FeatureStore(repo_path=store_dir)

    entity_rows = [
        {'sms_id': sms_id}
        for sms_id in sms_ids
    ]
    # Reading features through each of the feature services directly
    # (as opposed to: specifying explicitly a list of "feature_view:feature")
    _f_from_svc_1 = store.get_feature_service('labeled_sms_1')
    features_1 = store.get_online_features(features=_f_from_svc_1, entity_rows=entity_rows).to_df().to_dict()

    _f_from_svc_2 = store.get_feature_service('labeled_sms_2')
    features_2 = store.get_online_features(features=_f_from_svc_2, entity_rows=entity_rows).to_df().to_dict()

    for sms_idx, sms_id in enumerate(sms_ids):
        print(f'   SMS ID "{sms_id}"')
        print(f'      labeled_sms_1 ==> ', end='')
        if not _isnull(features_1['cap_r'][sms_idx]):
            print(f'cap_r = {features_1["cap_r"][sms_idx]}, [...] label = {features_1["label"][sms_idx]}')
        else:
            print('NOTHING FOUND')
        print(f'      labeled_sms_2 ==> ', end='')
        if not _isnull(features_2['features'][sms_idx]):
            print(f'features = {str(features_2["features"][sms_idx])[:12]}..., label = {features_2["label"][sms_idx]}')
        else:
            print('NOTHING FOUND')
