import json
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

from analysis.feature_extractor.feature_extractor import FeatureExtractor

base_dir = os.path.abspath(os.path.dirname(__file__))

input_dir = os.path.join(base_dir, '..', '..',  'models', 'model2_2020', 'tokenizer')
input_metadata_file = os.path.join(input_dir, 'settings.json')
input_tokenizer_file = os.path.join(input_dir, 'tokenizer.json')


class Feature2Extractor(FeatureExtractor):

    FEATURE_ORDERED_LIST = ...

    def __init__(self):
        self.tokenizer_metadata = json.load(open(input_metadata_file))
        self.tokenizer = tokenizer_from_json(open(input_tokenizer_file).read())
        self.FEATURE_ORDERED_LIST = [
            f'f_{idx:02}'
            for idx in range(self.tokenizer_metadata['MAX_SEQ_LENGTH'])
        ]

    def get_features(self, text):
        seqs = self.tokenizer.texts_to_sequences([text])
        padded = pad_sequences(
            seqs,
            maxlen=self.tokenizer_metadata['MAX_SEQ_LENGTH'],
        )[0]
        return {
            f: val
            for f, val in zip(self.FEATURE_ORDERED_LIST, padded)
        }


if __name__ == '__main__':
    import sys
    inp = ' '.join(sys.argv[1:])
    #
    f2_extractor = Feature2Extractor()
    #
    print('\nget_features:')
    print(f2_extractor.get_features(inp))
    print('\nget_feature_names:')
    print(f2_extractor.get_feature_names())
    print('\nget_features_list:')
    print(f2_extractor.get_features_list(inp))
