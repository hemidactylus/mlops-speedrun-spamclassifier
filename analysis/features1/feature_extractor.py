from nltk.tokenize import word_tokenize


_alphabet_up=list('QWERTYUIOPASDFGHJKLZXCVBNM')

cue_words = ['free', 'money', 'prize', 'win', 'won', 'winner', 'cash']

def _alphaonly(s):
    return ''.join(c for c in s if c.upper() in _alphabet_up)


def get_features1(text):
    #
    raw_tokens = list(word_tokenize(text))
    #
    tokens = [
        tok
        for tok in (
            _alphaonly(t)
            for t in raw_tokens
        )
        if tok
    ]
    #
    numchars = sum(len(t) for t in tokens)
    if numchars > 0:
        # capitalization ratio
        cap_r = sum(1 if c in _alphabet_up else 0 for t in tokens for c in t) / numchars
        # non-alphabetic ratio
        total_count = sum(len(t) for t in raw_tokens)
        nal_r = (total_count - numchars) / numchars
    else:
        cap_r = 0.0
        nal_r = 0.0
    #
    ltokset = {t.lower() for t in tokens}
    cw_scores = [
        0 if cw not in ltokset else 1
        for cw in cue_words
    ]
    #
    return {
        'cap_r': cap_r,
        'nal_r': nal_r,
        'cw_scores': cw_scores,
    }


if __name__ == '__main__':
    import sys
    inp = ' '.join(sys.argv[1:])
    print(get_features1(inp))
