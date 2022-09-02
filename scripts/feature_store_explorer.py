import os

from feast import FeatureStore

base_dir = os.path.abspath(os.path.dirname(__file__))
store_dir = os.path.join(base_dir, '..', 'sms_feature_store')

if __name__ == '__main__':
    #
    def _joinTags(tags):
        return ', '.join(
            f'{k}: {v}'
            for k, v in sorted(tags.items())
        )
    #
    def _describeFS(fs):
        if fs.description != '':
            desc = fs.description
        else:
            desc = None
        if fs.tags != {}:
            tgs = _joinTags(fs.tags)
        else:
            tgs = None
        parts = [p for p in [desc, tgs] if p]
        if len(parts):
            return f' ({"; ".join(parts)})'
        else:
            return ''
    #
    def _describeFD(f):
        if f.tags != {}:
            return f' ({_joinTags(f.tags)})'
        else:
            return ''
    #
    store = FeatureStore(repo_path=store_dir)
    print('FEATURE STORE ASSETS')
    for f_service in store.list_feature_services():
        print(f'  * Feature service: {f_service.name}{_describeFS(f_service)}')
        for fv_projection in f_service.feature_view_projections:
            print(f'        * Feature view projection: {fv_projection.name}')
            for feature in fv_projection.features:
                print(f'            * Feature: {feature.name:<18} [{str(feature.dtype):<12}]{_describeFD(feature)}')
