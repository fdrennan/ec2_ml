import tensorflow as tf

print(tf.__version__)

from tensorflow.keras.layers import Input, SimpleRNN, GRU, LSTM, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import SGD, Adam

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':

    # make the original data
    series = np.sin((0.1 * np.arange(400)) ** 2)

    """This is a time series of the form:

    $$ x(t) = \sin(\omega t^2) $$
    """

    # plot it
    plt.plot(series)
    plt.show()

    ### build the dataset
    # let's see if we can use T past values to predict the next value
    T = 10
    D = 1
    X = []
    Y = []
    for t in range(len(series) - T):
        x = series[t:t + T]
        X.append(x)
        y = series[t + T]
        Y.append(y)

    X = np.array(X).reshape(-1, T)  # make it N x T
    Y = np.array(Y)
    N = len(X)
    print("X.shape", X.shape, "Y.shape", Y.shape)

    ### try autoregressive linear model
    i = Input(shape=(T,))
    x = Dense(1)(i)
    model = Model(i, x)
    model.compile(
        loss='mse',
        optimizer=Adam(lr=0.01),
    )

    # train the RNN
    r = model.fit(
        X[:-N // 2], Y[:-N // 2],
        epochs=80,
        validation_data=(X[-N // 2:], Y[-N // 2:]),
    )

    # Plot loss per iteration
    import matplotlib.pyplot as plt

    plt.plot(r.history['loss'], label='loss')
    plt.plot(r.history['val_loss'], label='val_loss')
    plt.legend()

    # One-step forecast using true targets
    # Note: even the one-step forecast fails badly
    outputs = model.predict(X)
    print(outputs.shape)
    predictions = outputs[:, 0]

    plt.plot(Y, label='targets')
    plt.plot(predictions, label='predictions')
    plt.title("Linear Regression Predictions")
    plt.legend()
    plt.show()

    # This is the code we had before - it does the same thing

    # One-step forecast using true targets
    validation_target = Y[-N // 2:]
    validation_predictions = []

    # index of first validation input
    i = -N // 2

    while len(validation_predictions) < len(validation_target):
        p = model.predict(X[i].reshape(1, -1))[0, 0]  # 1x1 array -> scalar
        i += 1

        # update the predictions list
        validation_predictions.append(p)

    plt.plot(validation_target, label='forecast target')
    plt.plot(validation_predictions, label='forecast prediction')
    plt.legend()

    # Multi-step forecast
    validation_target = Y[-N // 2:]
    validation_predictions = []

    # first validation input
    last_x = X[-N // 2]  # 1-D array of length T

    while len(validation_predictions) < len(validation_target):
        p = model.predict(last_x.reshape(1, -1))[0, 0]  # 1x1 array -> scalar

        # update the predictions list
        validation_predictions.append(p)

        # make the new input
        last_x = np.roll(last_x, -1)
        last_x[-1] = p

    plt.plot(validation_target, label='forecast target')
    plt.plot(validation_predictions, label='forecast prediction')
    plt.legend()

    ### Now try RNN/LSTM model
    X = X.reshape(-1, T, 1)  # make it N x T x D

    # make the RNN
    i = Input(shape=(T, D))
    x = LSTM(10)(i)
    x = Dense(1)(x)
    model = Model(i, x)
    model.compile(
        loss='mse',
        optimizer=Adam(lr=0.05),
    )

    # train the RNN
    r = model.fit(
        X[:-N // 2], Y[:-N // 2],
        batch_size=32,
        epochs=200,
        validation_data=(X[-N // 2:], Y[-N // 2:]),
    )

    # plot some data
    plt.plot(r.history['loss'], label='loss')
    plt.plot(r.history['val_loss'], label='val_loss')
    plt.legend()
    plt.show()

    # One-step forecast using true targets
    outputs = model.predict(X)
    print(outputs.shape)
    predictions = outputs[:, 0]

    plt.plot(Y, label='targets')
    plt.plot(predictions, label='predictions')
    plt.title("many-to-one RNN")
    plt.legend()
    plt.show()

    # Multi-step forecast
    forecast = []
    input_ = X[-N // 2]
    while len(forecast) < len(Y[-N // 2:]):
        # Reshape the input_ to N x T x D
        f = model.predict(input_.reshape(1, T, 1))[0, 0]
        forecast.append(f)

        # make a new input with the latest forecast
        input_ = np.roll(input_, -1)
        input_[-1] = f

    plt.plot(Y[-N // 2:], label='targets')
    plt.plot(forecast, label='forecast')
    plt.title("RNN Forecast")
    plt.legend()
    plt.show()
