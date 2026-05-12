import numpy as np


# -----------------------------------
# PAD SEQUENCES
# -----------------------------------
def pad_sequences(
    sequences,
    max_len=10
):

    padded = []

    for seq in sequences:

        seq = seq[:max_len]

        seq += [0] * (
            max_len - len(seq)
        )

        padded.append(seq)

    return np.array(padded)