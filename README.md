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

Now to the setup: _TODO_.

- Add the repo's root to the Python path for your virtual env

## The story

### Chapter 1: 2019

#### Starting data

Our data engineers have collected a labeled set with three columns:
`sms_id`, `text` and `label`, the latter being simply `spam/ham`. This is in
`raw_data/raw_dataset.csv`.

> This dataset could realistically be stored on a database. For simplicity we keep it as a local file.

> The `raw_data/` directory plays the role of our own DWH, which we will
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
from analysis.features1.feature_extractor import get_features1
get_features1('You are A WINNER OF FREE CASH!!!!!!!')
# {'cap_r': 0.782608695652174, 'nal_r': 0.30434782608695654, 'cw_scores': [1, 0, 0, 0, 0, 1, 1]}
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

#### Setting up the Feast repo

It's time to set up the Feast feature repository. The Parquet files
we just created will be the offline sources, and - for later usage -
we will set Astra DB as the online store. This amounts to making sure
the right secrets appear in the `sms_feature_store/feature_store.yaml`
file.

> Copy the template `feature_store.yaml.template`
> with the right name, and make sure to enter your secrets, bundle file
> and keyspace name.

#### Training the first model ("2019-model")

Why did we go through this hassle with the feature store?
One of the reasons is that different teams can share standardized access
to the features and share them easily.

Now, indeed, another team in the company can take these features and train
the model by retrieving labels and features from the feature store.

