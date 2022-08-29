import os

# determine where in the 'story' we are
# (this makes the definitions here "dynamic" and is only a device to mimic
#  successive stages in refining the composition of the feature store).
FEAST_STORE_STAGE = os.environ.get('FEAST_STORE_STAGE', '2019')

from feast import Entity, FeatureService, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String, Array

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
features1_view = FeatureView(
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

if FEAST_STORE_STAGE in {'2020', '2021'}:
    # additional 'v2' stuff
    smss2 = FileSource(
        path=os.path.join(data_dir, 'sms_features2.parquet'),
        timestamp_field='event_timestamp',
    )
    features2_view = FeatureView(
        name='sms_features2',
        entities=[sms],
        schema=[
            Field(name='features', dtype=Array(Int64)),
        ],
        online=True,
        source=smss2,
        tags={},
    )
    labeled2 = FeatureService(
        name='labeled_sms_2',
        features=[
            features2_view,
            label_view,
        ],
    )

# feature services
labeled1 = FeatureService(
    name='labeled_sms_1',
    features=[
        features1_view,
        label_view,
    ],
)
