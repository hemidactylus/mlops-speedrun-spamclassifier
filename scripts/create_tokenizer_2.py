import os
import json
import pickle
import pandas as pd

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

# tokenizer settings. These will NOT be changed unless
# moving to a new model version.
MAX_NUM_WORDS = 180
MAX_SEQ_LENGTH = 30

base_dir = os.path.abspath(os.path.dirname(__file__))
offline_data_dir = os.path.join(base_dir, '..', 'offline_data')
raw_input_file = os.path.join(base_dir, '..', 'raw_data', 'raw_dataset.csv')

output_dir = os.path.join(base_dir, '..', 'models', 'model2_2020', 'tokenizer')
output_metadata_file = os.path.join(output_dir, 'settings.json')
output_tokenizer_file = os.path.join(output_dir, 'tokenizer.pkl')

if __name__ == '__main__':
    # read input training texts
    raw_df = pd.read_csv(raw_input_file)
    texts = raw_df['text'].tolist()
    # fit tokenizer
    tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)
    tokenizer.fit_on_texts(texts)

    # sample usage:
    def get_features_v2(text):
        # Input:  str
        # Output: plain fixed-len list of integers
        seqs = tokenizer.texts_to_sequences([text])
        padded = pad_sequences(seqs, maxlen=MAX_SEQ_LENGTH)[0]
        return padded.tolist()


    # usage test
    input_text = 'Hello, you can win free cash!'
    output_features = get_features_v2(input_text)
    print(f'INPUT "{input_text}')
    print(f'OUTPUT {output_features}')

    # persist the tokenizer and its metadata
    t_metadata = {
        'MAX_NUM_WORDS': MAX_NUM_WORDS,
        'MAX_SEQ_LENGTH': MAX_SEQ_LENGTH,
    }
    with open(output_metadata_file, 'w') as m_of:
        json.dump(t_metadata, m_of, indent=2)
    with open(output_tokenizer_file, 'wb') as t_of:
        pickle.dump(tokenizer, t_of)

    print('Tokenizer persisted to:')
    print('    - ' + output_metadata_file)
    print('    - ' + output_tokenizer_file)
    