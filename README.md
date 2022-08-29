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
python analysis/features1/feature1_extractor.py \
  You are A WINNER OF FREE CASH\!\!\!\!\!\!
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
FEAST_STORE_STAGE=2019 feast -c sms_feature_store apply
```

the local registry will be updated with the feature definitions
found in `sms_feature_store/feature_definitions.py`, and
in the online store (Astra DB) the tables for each feature view
will be created (empty for the time being).

> _Note_: we pass an environment variable to Feast commands
> to emulate the "evolution over time" of the feature-store definitions.
> In a real application, this should generally not be needed.

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

We are about to launch our first app. In the spirit of microservices,
there will be _two_ separate APIs behind the front-end.

The first is tasked with serving the model. It has endpoints
to convert a text into features, to convert features into a prediction,
and one which combines the two and makes a text directly into a prediction.

The API, implemented with FastAPI, is written in a modular way in
order to serve several versions
of various models using the same (version-prefixed) endpoint pattern.
This is achieved by wrapping
the model (as stored during training) in a specific class, which in turn
subclasses a generic `TextClassifierModel` interface; instances of these
classes, one per model/version, are given to a factory function that creates
a corresponding FastAPI "router".

At this stage, we can only serve model `v1`. To start the API,
```
SPAM_MODEL_VERSIONS="v1" uvicorn api.model_serving.model_serving_api:app
```

and to test it you can try:
```
curl -XPOST \
  http://localhost:8000/model/v1/text_to_features \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'

curl -XPOST \
  http://localhost:8000/model/v1/features_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"features": [0.09090909090909091,0.0,0,0,0,0,0,0,0]}'

curl -XPOST \
  http://localhost:8000/model/v1/text_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'
```

You can also check the auto-generated OpenAPI docs: `http://127.0.0.1:8000/docs`.

Note that in principle this API could be used not only by the front-end (text-to-prediction, presumably), but also by backend services tasked with writing rows to a feature store
from the raw input SMS text.

TODO:

- cache
- call log
- (cache-aware) multiple input endpoint

#### The user-data API

The other API, kept as a separate service out of cleanliness,
will handle the data of our app users. This app is a simple
SMS service, whereby users can visualize their inbox.

> Throughout this demo, of course, security, authentication and other matters
> are ignored for the sake of simplicity. _Don't do this in production._

The API has endpoints to retrieve the messages stored as belonging to
(as in "received by") a given
user's inbox (either all of them or one by one by their message ID).

The data is stored on an Astra DB table, with a simple structure: there are
columns `user_id` (recipient), `sms_id` (a time-ordered unique TIMEUUID),
`sender_id` and `sms_text`. The primary key is `(( user_id ), sms_id)`,
with a partitioning that makes it easy to retrieve all messages for a given
user at once.

> Notes: (1) for more on partitioning in Cassandra and Astra DB, we recommend
> the workshop about ["Data Modeling"](https://github.com/datastaxdevs/workshop-cassandra-data-modeling). (2) In a real production app,
> mitigation techniques would be put in place to prevent partitions from growing
> too large (i.e. if a user starts hoarding enormous amounts of messages).
> (3) Here, for simplicity, we'll keep the table in the same keyspace as the
> rest of the architecture: such a choice might not be optimal in a real app.
> (4) User IDs would be better defined as type UUID, but here we wanted to
> keep things simple.

First provide the Astra DB credentials by copying file `.env.sample` to `.env`
and filling the required values (much like you did for the feature-store
YAML file above).

Now you can run this script to create the table and populate it with
sample data:
```
python scripts/initialize_user_api_data.py
```

> Tip: you can check the data with the following CQL query:
> `SELECT sms_id, toDate(sms_id), sender_id, sms_text FROM smss_by_users WHERE user_id='max';`.

The user-data API can now be started in another shell
(also on a different port than the other API):
```
uvicorn api.user_data.user_api:app --port 8111
```

You can test it with:
```
curl http://localhost:8111/sms/max

curl http://localhost:8111/sms/fiona/32e14000-8400-11e9-aeb7-d19b11ef0c7e
```

(and see the docs at `http://localhost:8111/docs` as well.)

#### The frontend

The Web app is a simple React app where users "login" by entering their name
and can see their inbox. For each SMS, they can reach the spam-detection API
and get an assessment on the message text (by clicking on the
magnifying-glass icons).

To start the client:
```
cd client/sms_web_app
npm install
REACT_APP_SPAM_MODEL_VERSION=v1 npm start
```

(note that we pass the model version to reach in the Spam API),
then open `http://localhost:3000/` in the browser.

>*Tip*: enter `fiona` or `max` as "username", to see some SMS messages.

### Chapter 2: 2020

#### A new spam model

It's 2020, and the data science team decides to train a new, better model from
scratch using the same labels. The model, however, is radically different,
and the required features differ too.
The plan is to use a LSTM recurrent neural network, and a Tensorflow
`Tokenizer` to convert the text to the feature list.

The tokenizer is first
fitted on the training set and then persisted to file, so to have it
available when later exposing the "text to features" capability of the model.

Run
```
python scripts/create_tokenizer_2.py
```
to achieve the above. As a result, the tokenizer file (and associated metadata)
will be created in `models/model2_2020/tokenizer/`.

As was done for the features "v1", the text-to-features mapping,
which loads and uses the just-stored tokenizer, is made available as a
standardized class (compliant with the same generic `FeatureExtractor`
interface as the previous version) and can be checked with:
```
python analysis/features2/feature2_extractor.py \
  You are A WINNER OF FREE CASH\!\!\!\!\!\!
```

#### A new feature view in Feast

Similarly to what was done for the "2019" (or "v1") features,
a local-storage (Parquet-file-based) source is created and the
Feast store is updated so that it reflects the presence of
a new feature view and feature service (the one pairing the labeled
set with the new "v2" feature vector).

First the Parquet file is generated by calculating the features for
all of the training data:
```
python scripts/create_offline_sources_2.py
```

Then a new `FileSource`, `FeatureView` and `FeatureService` are added to `sms_feature_store/feature_definitions.py`
(check usage of `FEAST_STORE_STAGE`
there for more details) and finally the updated repository is "applied" again,
so that the changes are reflected to both the registry and the online-store
data structures (viz. Astra DB tables):
```
FEAST_STORE_STAGE=2020 feast -c sms_feature_store apply
```

_Note that this time the "features" are a single field in the feature view,
a field of type `Array(Int64)` in Feast parlance._

#### Training the model

It is now time to create the model and train it. This requires devising
the network architecture, re-casting the labels with one-hot-encoding,
and start with the actual training.

As usual, this is done in a notebook: _to complete_