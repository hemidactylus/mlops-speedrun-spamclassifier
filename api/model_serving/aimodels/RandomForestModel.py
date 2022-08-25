import pandas
import joblib

class RandomForestModel():

    def __init__(self, model_path, feature_extractor, output_labels):
        self.feature_extractor = feature_extractor
        self.output_labels = output_labels
        self.model_path = model_path
        #
        self.model = joblib.load(self.model_path)

    def text_to_features(self, text):
        return self.feature_extractor.get_features_list(text)

    def features_to_prediction(self, features):
        # features = a list
        predicted_idx = self.model.predict(pandas.DataFrame({
            k: [v]
            for k, v in zip(
                self.feature_extractor.FEATURE_ORDERED_LIST,
                features,
            )
        }))[0]
        return {
            lab: 1 if idx == predicted_idx else 0
            for idx, lab in enumerate(self.output_labels)
        }

    def text_to_prediction(self, text):
        return self.features_to_prediction(self.text_to_features(text))
