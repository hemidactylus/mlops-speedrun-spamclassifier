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
- Copy `sms_feature_store/feature_store.yaml.template` to `sms_feature_store/feature_store.yaml` and replace your Astra DB values _(Note: in real life you probably would have run `feast init sms_feature_store -t cassandra` and have followed the interactive procedure)_

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

As usual, this is done in a notebook: running all of
```
training/model2_2020/train_model_2_2020.ipynb
```
will result in the model being stored, for later usage, in
`models/model3_2021/classifier`.

#### Extending the model-serving API

Now in order to upgrade the model-serving API so that it can also
expose the new model ("v2", i.e. the 2020 model, including its feature
extractor) all we need to do is to create the `KerasLSTMModel` subclass
of `TextClassifierModel` and wire it to the API with the dynamic
FastAPI router factory used already for `"v1"`.
See file `api/model_serving/aimodels/KerasLSTMModel.py` and
the `"v2"` part in `api/model_serving/model_serving_api.py`. To start the API with
both models:
```
SPAM_MODEL_VERSIONS="v1,v2" uvicorn api.model_serving.model_serving_api:app
```

and to test the endpoints for the new model:

```
curl -XPOST \
  http://localhost:8000/model/v2/text_to_features \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'

curl -XPOST \
  http://localhost:8000/model/v2/features_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"features": [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                    0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                    0.0,0.0,0.0,0.0,0.0,1.0,20.0,4.0]}'

curl -XPOST \
  http://localhost:8000/model/v2/text_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'
```

#### Client test for "v2"

Provided both API services are running (remember
`uvicorn api.user_data.user_api:app --port 8111`), this is simply:
```
REACT_APP_SPAM_MODEL_VERSION=v2 npm start
```


### Chapter 3: 2021

#### A new model on old features

The data science team decides to take the challenge again
and starts building a new, more accurate spam detection model,
which will be "v3" a.k.a. "2021".

> *Hint*: it may well have been another team doing this: having a feature store
> as a central "hub" indeed enables feature discovery across teams. Check the
> script `python scripts/feature_store_explorer.py` to see how the feature store
> can be directly inspected to look for existing features.

They decide to start from the same features as the previous model, though:
In the spirit of this demo, this is also to emphasize the modularity
of the moving parts at play:

- no need for new elements in the feature store
- the spam-detection API will have a new "v3" set of endpoints, combining the same feature extractor as "v2" with a new trained model.

This model will be an improvement over "v2", with a similar architecture (LSTM recurrent neural network
with slightly different parameters). Training will take place, similarly as before, by running the notebook
```
training/model3_2021/train_model_3_2021.ipynb
```

and, as a result, the model will be stored in `models/model3_2021/classifier` (no need for a separate `tokenizer` directory as it'll use the one from v2).

Similarly as what was done for "v2", a new set of "v3" routes
is added to the model-serving API, which can now be started
as:
```
SPAM_MODEL_VERSIONS="v1,v2,v3" uvicorn api.model_serving.model_serving_api:app
```

and tested with:
```
curl -XPOST \
  http://localhost:8000/model/v3/text_to_features \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'

curl -XPOST \
  http://localhost:8000/model/v3/features_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"features": [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                    0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                    0.0,0.0,0.0,0.0,0.0,1.0,20.0,4.0]}'

curl -XPOST \
  http://localhost:8000/model/v3/text_to_prediction \
  -H 'Content-Type: application/json' \
  -d '{"text": "I have a dream"}'
```

As for the client, it can be made to point to the new model with:
```
REACT_APP_SPAM_MODEL_VERSION=v3 npm start
```
(if the user-data API is also running, `uvicorn api.user_data.user_api:app --port 8111`).

#### Toward real-time

Now the company wants to improve the service to the users
by adding ingestion of new SMS messages into the app.

To continue adhering to a microservice approach, there will be yet another API,
the "Inbox API", tasked with offering to external actors
(such as the telephone company) an endpoint to insert new messages
into our system. This webhook will take care, internally, of everything
needed to deal with the arrival of a new message.

So far, we have used
Feast's "offline feature store" capability, i.e. specialized methods to
retrieve point-in-time data from what essentially is a time-series warehouse.
Now it's time to start using the **online store**: a low-latency data store
where the latest features for any given entity are saved for fast retrieval.
In practice, while the offline store contains the whole time series (the "history")
of the feature values for an entity, the online store is where only the most
up-to-date entry will be kept.

There are various ways to "refresh" the online store. One such approach is to
manually invoke the "materialize" operation, which will scan the offline store
(starting from the last materialization done so far) and transport the data over
to the online store.
There are plugins to use several databases as online store: as can be seen in
`sms_feature_score/feature_store.yaml`, we are using Astra DB.

> The rationale behind keeping the latest features in the online store, in our
> case, is that computing the features can be expensive to do in real-time when
> the user needs them, so we prefer to pre-compute them
> as soon as the new raw data comes in. Other valid solutions might involve
> enqueueing their computation, for instance in a Pulsar topic, for consumption
> as a background asynchronous task. See toward the end for a sketch of such
> a solution, based on CDC, Astra Streaming and Pulsar functions.

Materialization is invoked with an explicit date parameter: it will consider
all offline data up to that moment, "as if time stopped at the provided date".
Imagine your user data (features) change over time, such as a
"last 10 items purchased" metric. These, at each user interaction, would be
accumulated in a time-series fashion (in our case, in the parquet files).
By scheduling a periodic (incremental) materialization, one makes sure that
the online store gets updated and contains the latest value for this metric.
The online store can then be queried to quickly obtain an up-to-date feature
set, ready for real-time prediction.

#### Materialize

We have a tiny script that tries to fetch "v1" and "v2" features from the
online store, and we'll use it in this section to illustrate what's going on.
Try running
```
python scripts/online_store_sampler.py 14050 14051 14052
```
and you should see that nothing is found (yet!) on the online store for any
feature service.

Now we'll pretend for a moment that it's still 2019 and we materialize
from "the beginning of time" to the end of the year. This should catch all
and only the entries in the "v1" feature set (along with the label set)
and transport them over to the online store:
```
feast -c sms_feature_store materialize 2009-01-01T00:00:00 2019-12-31T00:00:00
```
_(Note: this process is considered an "exceptional" bulk operation; don't worry
if it takes many tens of minutes!)_

Running the online sampler script now,
```
python scripts/online_store_sampler.py 14050 14051 14052
```
will show that the `labeled_sms_1` features are found in the online store,
while the `labeled_sms_2` (created in 2020) are not there yet.

Now it's time to do an incremental materialize step and bring the
online store up to date:
```
feast -c sms_feature_store materialize-incremental 2021-09-02T00:00:00
```

The reading script will now find features for both feature services.

_As remarked above, we could content ourselves with a new-message-ingestion
process that writes to the offline store, and a scheduled materialization
to have the features ready to be served to the app. But we want to do better..._

Feast provides two very interesting tools to make our app more streamlined:
a feature server and push sources. Let's see how they can become part of
our production pipeline and get us closer to a real-time architecture.

#### Feature server

Most operations on a Feast store can be exposed by the "feature server", which
is an HTTP API wrapping the core operations. To start it, you can simply run:

```
feast -c sms_feature_store serve
```
Now you can start querying it (the default port is 6566) to retrieve feature values,
either asking for an explicit list of features from one or more feature views:
```
curl -s -X POST \
  http://127.0.0.1:6566/get-online-features \
  -d  '
        {
            "features": [
                "sms_features1:cap_r",
                "sms_labels:label"
            ],
            "entities": {
                "sms_id": [
                    14050,
                    14051,
                    14052
                ]
            }
        }
      '
```
or directly specifying a feature service:
```
curl -s -X POST \
  http://127.0.0.1:6566/get-online-features \
  -d  '
        {
            "feature_service": "labeled_sms_2",
            "entities": {
                "sms_id": [
                    14050,
                    14051,
                    14052
                ]
            }
        }
      '
```

#### Push sources

Another crucial element in Feast are _push sources_. These, which get
"attached" to regular sources, allow for dynamic pushing of new entity
rows (with their features) and, combined with the above HTTP feature server,
make it possible to use Feast as infrastructure for inserting new data into
the store in real-time.

We'll enable a push source for our "v2" features, with the goal of using
it to handle the real-time architecture described above with these features
pre-computed and ready to be used in user-initiated predictions.

We start by altering the feature definitions for the store: until now we had
the `FileSource` wired to the `FeatureView` through the `source` parameter in the latter
(namely `smss2 -> features2_view`); now we'll have a chain
`FileSource -> PushSource -> FeatureView`, i.e.
```
smss2 -> smss2_push -> features2_view
```
The nice thing is that once we have this setup, anything we push will be
automatically propagated along this chain.

The changes are encoded in the `sms_feature_store/feature_definitions.py`
once we set the environment variable `FEAST_STORE_STAGE=2021`, so now we need
to run
```
FEAST_STORE_STAGE=2021 feast -c sms_feature_store apply
```

Make sure the feature server is restarted (`Ctrl-C` and then re-run
the `feast -c sms_feature_store serve` command).

We can now *push new entity rows to the feature store* directly through
the feature server. The following command will push a newer version
of the "v2" features for the SMS with `sms_id=14052`, _both to the offline
and the online store_:

```
curl -X POST "http://localhost:6566/push" -d '{
    "push_source_name": "smss2_push",
    "df": {
            "sms_id": [14052],
            "event_timestamp": ["2021-09-02 00:00:00"],
            "features": [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,65,65,108,2,30]]
    },
    "to": "online_and_offline"
  }'
```

Let us check the online store with the script:
```
python scripts/online_store_sampler.py 14052
```
and by querying the server:
```
curl -s -X POST \
  http://127.0.0.1:6566/get-online-features \
  -d  '
        {
            "feature_service": "labeled_sms_2",
            "entities": {
                "sms_id": [14052]
            }
        }
      '
```

In short:

- the offline store has received a new line in its time-series, with more recent timestamp;
- in the online store, the entry for that SMS and for features "v2" has been overwritten and is ready to be used.

This bypasses the need to run (scheduled or otherwise) an explicit materialization step.

> _Note_: This write is just for demonstration purposes: the new
> feature values make little sense in
> themselves. Still, this will be harmless - even if we were to repeat the
> training step, the point-in-time offline feature retrieval would not fetch
> this update as its date is beyond its `training_timefreeze`; and the SMS
> messages from the training set will not be used anywhere else in the app.

#### App architecture II

It is now time to revise the app and take advantage of the feature server.
The changes are as follows:

- the "Inbox API", when receiving a new message, will:
  + contact the model-serving API to get the "v2" features;
  + contact the feature server to push them to the feature store, for later online usage;
  + write the SMS to the database table for the user-data API.
- the client will ask the feature server for the features of a SMS, based on its `sms_id`.
- it will then query the `features_to_prediction` endpoint in the model-serving API to get the ham/spam status of a message;
- (we need a backfill job to prepare the `labeled_sms_2` features for the messages that are already in the inbox);
