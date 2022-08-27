import os
import datetime
import pandas as pd

from analysis.features1.feature1_extractor import Feature1Extractor

base_dir = os.path.abspath(os.path.dirname(__file__))
offline_data_dir = os.path.join(base_dir, '..', 'offline_data')

raw_input_file = os.path.join(base_dir, '..', 'raw_data', 'raw_dataset.csv')
feature_output_file = os.path.join(offline_data_dir, 'sms_features1.parquet')
label_output_file = os.path.join(offline_data_dir, 'sms_labels.parquet')

if __name__ == '__main__':
    #
    raw_df = pd.read_csv(raw_input_file)
    raw_df['event_timestamp'] = datetime.datetime(2019, 2, 3)

    #
    f1_extractor = Feature1Extractor()
    feature_list = f1_extractor.FEATURE_ORDERED_LIST
    #
    raw_df['features'] = raw_df['text'].map(f1_extractor.get_features)
    # flatten the features for readability
    for fea_k in feature_list:
        raw_df[fea_k]=raw_df['features'].map(lambda f: f[fea_k])

    # select
    fea_df = raw_df[['event_timestamp', 'sms_id'] + feature_list]
    lab_df = raw_df[['event_timestamp', 'sms_id', 'label']]

    fea_df.to_parquet(feature_output_file)
    lab_df.to_parquet(label_output_file)

    print('Done (%s ==> %s, %s)' % (
        raw_input_file,
        feature_output_file,
        label_output_file,
    ))
