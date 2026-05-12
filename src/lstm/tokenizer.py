from collections import Counter


# -----------------------------------
# BUILD VOCAB
# -----------------------------------
def build_vocab(dataset):

    counter = Counter()

    for item in dataset:

        for token in item["sequence"]:

            counter[token] += 1

    vocab = {

        "<PAD>": 0,
        "<UNK>": 1
    }

    idx = 2

    for token in counter:

        vocab[token] = idx

        idx += 1

    return vocab


# -----------------------------------
# ENCODE SEQUENCE
# -----------------------------------
def encode_sequence(
    sequence,
    vocab
):

    encoded = []

    for token in sequence:

        encoded.append(

            vocab.get(
                token,
                vocab["<UNK>"]
            )
        )

    return encoded