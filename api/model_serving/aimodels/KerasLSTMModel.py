import json
from operator import itemgetter
from tensorflow.keras import models
import numpy as np
from api.model_serving.aimodels.TextClassifierModel import TextClassifierModel


class KerasLSTMModel(TextClassifierModel):

    def __init__(self, model_path, model_metadata_path, feature_extractor):
        self.feature_extractor = feature_extractor
        self.model = models.load_model(model_path)
        self.metadata = json.load(open(model_metadata_path))
        #
        self.output_labels = [
            kpair[0]
            for kpair in sorted(
                self.metadata['label_legend'].items(),
                key=itemgetter(1),
            )
        ]


    def text_to_features(self, text):
        return self.feature_extractor.get_features_list(text)

    def features_to_prediction_vector(self, features):
        return self.model.predict(np.array([features]))[0].tolist()
