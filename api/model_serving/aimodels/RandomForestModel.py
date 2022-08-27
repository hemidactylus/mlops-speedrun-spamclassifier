import pandas
import joblib

from api.model_serving.aimodels.TextClassifierModel import TextClassifierModel

class RandomForestModel(TextClassifierModel):

    def __init__(self, model_path, feature_extractor, output_labels):
        self.feature_extractor = feature_extractor
        self.output_labels = output_labels
        self.model_path = model_path
        #
        self.model = joblib.load(self.model_path)

    def text_to_features(self, text):
        return self.feature_extractor.get_features_list(text)

    def features_to_prediction_vector(self, features):
        # features = a list
        predicted_idx = self.model.predict(pandas.DataFrame({
            k: [v]
            for k, v in zip(
                self.feature_extractor.FEATURE_ORDERED_LIST,
                features,
            )
        }))[0]
        return [
            1 if idx == predicted_idx else 0
            for idx in range(len(self.output_labels))
        ]
