import os
import datetime
import pandas as pd

from analysis.features2.feature2_extractor import Feature2Extractor

base_dir = os.path.abspath(os.path.dirname(__file__))
offline_data_dir = os.path.join(base_dir, '..', 'offline_data')

raw_input_file = os.path.join(base_dir, '..', 'raw_data', 'raw_dataset.csv')
feature_output_file = os.path.join(offline_data_dir, 'sms_features2.parquet')

if __name__ == '__main__':
    #
    raw_df = pd.read_csv(raw_input_file)
    raw_df['event_timestamp'] = datetime.datetime(2020, 4, 5)

    #
    f2_extractor = Feature2Extractor()
    #
    raw_df['features'] = raw_df['text'].map(f2_extractor.get_features_list)

    # select
    fea_df = raw_df[['event_timestamp', 'sms_id', 'features']]

    fea_df.to_parquet(feature_output_file)

    print('Done (%s ==> %s)' % (
        raw_input_file,
        feature_output_file,
    ))
