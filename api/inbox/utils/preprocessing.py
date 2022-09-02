# Preprocessing after the feature extractor step and before calling feast store

def _adjust_feature_map_for_store(f_map0, f_model_version):
    if f_model_version == 'v3':
        # input is {'features': [list of floats]}
        # output must be {'features': [list of integers]}
        if 'features' in f_map0:
            return {
                'features': [[int(fv) for fv in f_map0['features']]],
            }
        else:
            return None
    else:
        raise NotImplementedError
