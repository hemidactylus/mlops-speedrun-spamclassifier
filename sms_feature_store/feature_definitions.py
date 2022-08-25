import os

from feast import Entity, FeatureService, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

base_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, '..', 'offline_data')

# entities
sms = Entity(name='sms', join_keys=['sms_id'])

# sources
smss1 = FileSource(
    path=os.path.join(data_dir, 'sms_features1.parquet'),
    timestamp_field='event_timestamp',
)

labels = FileSource(
    path=os.path.join(data_dir, 'sms_labels.parquet'),
    timestamp_field='event_timestamp',
)

# feature views
text_view = FeatureView(
    name='sms_features1',
    entities=[sms],
    schema=[
        Field(name='cap_r', dtype=Float32),
        Field(name='nal_r', dtype=Float32),
    ] + [
        Field(name='cw_scores_%i' % i, dtype=Int64)
        for i in range(7)
    ],
    online=True,
    source=smss1,
    tags={},
)

label_view = FeatureView(
    name='sms_labels',
    entities=[sms],
    schema=[
        Field(name='label', dtype=String),
    ],
    online=True,
    source=labels,
    tags={},
)

# feature services
labeled1 = FeatureService(
    name='labeled_sms_1',
    features=[
        text_view,
        label_view,
    ],
)
