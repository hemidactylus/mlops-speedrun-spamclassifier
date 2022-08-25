class FeatureExtractor():

    def get_features_list(self, text):
        fdict = self.get_features(text)
        return [
            fdict[k]
            for k in self.FEATURE_ORDERED_LIST
        ]

    def get_feature_names(self):
        return self.FEATURE_ORDERED_LIST
