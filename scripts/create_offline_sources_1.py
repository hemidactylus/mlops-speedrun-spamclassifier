import os
import datetime
import pandas as pd

from analysis.features1.feature_extractor import get_features1

base_dir = os.path.abspath(os.path.dirname(__file__))
offline_data_dir = os.path.join(base_dir, '..', 'offline_data')

raw_input_file = os.path.join(base_dir, '..', 'raw_data', 'raw_dataset.csv')
feature_output_file = os.path.join(offline_data_dir, 'sms_features1.parquet')
label_output_file = os.path.join(offline_data_dir, 'sms_labels.parquet')

#
raw_df = pd.read_csv(raw_input_file)

raw_df['event_timestamp'] = datetime.datetime(2019, 2, 3)

#
raw_df['features'] = raw_df['text'].map(get_features1)
#
raw_df['cap_r']=raw_df['features'].map(lambda f: f['cap_r'])
raw_df['nal_r']=raw_df['features'].map(lambda f: f['nal_r'])
for i in range(7):
    raw_df['cw_scores_%i' % i]=raw_df['features'].map(lambda f: f['cw_scores'][i])

# select
fea_df = raw_df[['event_timestamp', 'sms_id', 'cap_r', 'nal_r'] + ['cw_scores_%i' % i for i in range(7)]]
lab_df = raw_df[['event_timestamp', 'sms_id', 'label']]

fea_df.to_parquet(feature_output_file, compression=None)
lab_df.to_parquet(label_output_file, compression=None)

print('Done (%s ==> %s, %s)' % (
    raw_input_file,
    feature_output_file,
    label_output_file,
))
