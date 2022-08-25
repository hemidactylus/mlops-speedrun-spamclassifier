# MLOps speedrun: spam classifier

## Overview

We follow the MLOps story of a company working
on an application offering a service of spam detection
for SMS to their users.

The core problem is: creating spam detectors and making them available
within the application/as APIs. Emphasis on the production (or pseudo-production)
aspects, more than the accuracy of the ML itself.

We'll follow a fictional year-by-year story arc, as the architecture gets
progressively refined.

## Setup

In order to reproduce all steps yourself, you need to clone this repo,
create your database instance, and provide some secrets through dot-env
files and the like. To avoid excessive infrastructure overhead, some
components will be mocked with local (non-production) equivalents.

- Create a Python 3.8+ virtualenv and `pip install -r requirements.txt` into it.
- Add the repo's root to the Pythonpath of the virtualenv
- **TEMP** Take care of installing a certain commit of Feast in development mode, see instructions in `requirements.txt`
- Copy `sms_feature_store/feature_store.yaml.template` to `sms_feature_store/feature_store.yaml` and replace your Astra DB values

## The story

### Chapter 1: 2019

#### Starting data

Our data engineers have collected a labeled set with three columns:
`sms_id`, `text` and `label`, the latter being simply `spam/ham`. This is in
`raw_data/raw_dataset.csv`.

> This dataset could realistically be stored on a database.
> The `raw_data/` directory here plays the role of our own DWH, which we will
> later "connect" to the feature store for our own convenience.

_Note: in order to
create a labeled dataset of around 7.5K messages marked as spam/ham,
two different (publicly available) sets have been merged
(namely [this one](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
and [this one](https://archive.ics.uci.edu/ml/datasets/YouTube+Spam+Collection),
made available by the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/index.php))._

#### Features 1

Our feature engineers, after some exploratory analysis, have identified
a set of relevant features to build a classifier on.
The extraction of the features from the text is conveniently packed
in function `get_features1` of `analysis/features1/feature_extractor`.

```
from analysis.features1.feature1_extractor import Feature1Extractor
sample_text = 'You are A WINNER OF FREE CASH!!!!!!!'
f1_extractor = Feature1Extractor()
print(f1_extractor.get_features(sample_text))
print(f1_extractor.get_feature_names())
print(f1_extractor.get_features_list(sample_text))
```

#### Offline repository for features 1

Our data engineers want to keep all offline data in one place: for this, they
choose to use Feast. There will be a source for labels, and one for the features.
The key used to join the two tables will be the SMS id.

> To keep things simple Feast will use the local, file-based offline store,
> which means Parquet files to store data. In the same spirit, the feature
> registry will be a local SQLite database. In an actual production environment,
> the offline store would presumably be a remote database (such as BigQuery).
> Likewise, the store registry would better be stored in the cloud (e.g. on GCS):
> this would enable a workflow where different teams simply clone the project's
> repo and start working on the shared registry.

Run this script to generate the Parquet files which will serve as offline sources to Feast:

```
python scripts/create_offline_sources_1.py
```

Two Parquet files are created in `offline_data/`, one with the labels and
the other with the features, ready to be used as training set.

All rows in each Parquet file bears the same `event_timestamp`
(some time in 2019). This is secondary in this case, but would
be relevant if these data did get updated somehow, to allow
for time-travel-consistency in retrieving historical data.

#### Setting up the Feast repo

It's time to set up the Feast feature repository. The Parquet files
we just created will be the offline sources, and - for later usage -
we will set Astra DB as the online store. This amounts to making sure
the right secrets appear in the `sms_feature_store/feature_store.yaml`
file.

> Copy the template `feature_store.yaml.template`
> with the right name, and make sure to enter your secrets, bundle file
> and keyspace name.

Now, with this Feast CLI command,

```
feast -c sms_feature_store apply
```

the local registry will be updated with the feature definitions
found in `sms_feature_store/feature_definitions.py`, and
in the online store (Astra DB) the tables for each feature view
will be created (empty for the time being).

#### Training the first model ("2019-model")

Why did we go through this hassle with the feature store?
One of the reasons is that different teams can share standardized access
to the features and share them easily.

Now, indeed, another team in the company can take these features and train
the model by retrieving labels and features from the feature store.

The data scientists can indeed start reading features from the feature
store, the set of `sms_id` to use for training, and create the
"2019" spam-detection model. Since they like to work with interactive notebooks,
here's what you do:

- start `jupyter notebook`
- locate `training/model1_2019/train_model_1_2019.ipynb`
- run it all the way to storing the trained model. 

> **Note**: the details of the (rather sketchy) training process are not the focus of this story and will not be examined particularly.

The notebook accesses the Feast store and uses it to retrieve, from offline
storage, the training data. To do so, the join on `sms_id` is done behind
the scenes to give a dataset with features _and_ labels. Note we specify
a date, to ensure we retrieve historically-consistent data ("as if time was
frozen on that day").

Once the data is transformed and the model is trained,
it is saved (using `joblib`) to file `models/model1_2019/model1.pkl`
for later usage.

> In a production environment, the model would be stored e.g. on cloud object
> storage; moreover, if the feature registry were not just a local SQLite, this
> part of the story could well be played on another machine, provided this
> repo is there with all secrets set up.

#### Serving the model in production (2019)

A first API "v1" able to process text as well as a featurelist,
subjecting it to the model.
Also it handles feature extraction.

A second API doing the menial work of "ordinarily serving the app"


TODO:

- an app with a simple users-sms-text backing table, via API
- an API exposing the model (versioned url paths)
- a simple react frontend to demo this
