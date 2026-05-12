import numpy as np

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    classification_report
)

from tensorflow.keras.models import Sequential

from tensorflow.keras.layers import (
    Embedding,
    LSTM,
    Dense,
    Dropout
)

from tensorflow.keras.utils import (
    to_categorical
)

from src.lstm.tokenizer import (
    tokenize_sequences
)


# -----------------------------------
# TRAIN LSTM
# -----------------------------------
def train_lstm(
    X,
    y
):

    X, tokenizer = tokenize_sequences(X)

    y = np.array(y)

    vocab_size = len(
        tokenizer.word_index
    ) + 1

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.2,

        random_state=42
    )

    # -----------------------------------
    # MODEL
    # -----------------------------------
    model = Sequential([

        Embedding(
            input_dim=vocab_size,
            output_dim=32,
            input_length=X.shape[1]
        ),

        LSTM(
            64,
            return_sequences=False
        ),

        Dropout(0.2),

        Dense(
            32,
            activation="relu"
        ),

        Dense(
            1,
            activation="sigmoid"
        )
    ])

    model.compile(

        optimizer="adam",

        loss="binary_crossentropy",

        metrics=["accuracy"]
    )

    # -----------------------------------
    # TRAIN
    # -----------------------------------
    model.fit(

        X_train,
        y_train,

        epochs=5,

        batch_size=32,

        validation_split=0.1
    )

    # -----------------------------------
    # EVALUATE
    # -----------------------------------
    preds = model.predict(X_test)

    preds = (preds > 0.5).astype(int)

    print(

        classification_report(
            y_test,
            preds
        )
    )

    return (
        model,
        tokenizer
    )