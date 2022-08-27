class TextClassifierModel():

    # must be ['label1', 'label2', ... 'labeln']
    output_labels = ...

    def text_to_features(self, text):
        # must return [f1, f2, ... fn]
        ...

    def features_to_prediction_vector(self, features):
        # must return [prob1, prob2, ... probn]
        ...

    def text_to_prediction_vector(self, text):
        return self.features_to_prediction_vector(self.text_to_features(text))

    def features_to_prediction(self, features):
        '''
        return {label: prob}
        '''
        pred_vector = self.features_to_prediction_vector(features)
        return {
            lab: prob
            for lab, prob in zip(self.output_labels, pred_vector)
        }

    def text_to_prediction(self, text):
        '''
        return {label: prob}
        '''
        pred_vector = self.text_to_prediction_vector(text)
        return {
            lab: prob
            for lab, prob in zip(self.output_labels, pred_vector)
        }
