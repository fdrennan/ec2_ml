import tensorflow as tf
# More imports
from tensorflow.keras.layers import Input, LSTM, GRU, SimpleRNN, Dense, GlobalMaxPool1D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import SGD, Adam

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

if __name__ == '__main__':
    # yes, you can read dataframes from URLs!
    df = pd.read_csv('https://raw.githubusercontent.com/lazyprogrammer/machine_learning_examples/master/tf2.0/sbux.csv')

    AWS = os.getcwd().find('ubuntu') > 0
    if AWS:
        df.to_csv('/root/sbux.csv')
        df.to_csv('/root/sbux_2.csv')

    df.head()

    df.tail()

    # Start by doing the WRONG thing - trying to predict the price itself
    series = df['close'].values.reshape(-1, 1)

    # Normalize the data
    # Note: I didn't think about where the true boundary is, this is just approx.
    scaler = StandardScaler()
    scaler.fit(series[:len(series) // 2])
    series = scaler.transform(series).flatten()

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

    X = np.array(X).reshape(-1, T, 1)  # Now the data should be N x T x D
    Y = np.array(Y)
    N = len(X)
    print("X.shape", X.shape, "Y.shape", Y.shape)

    ### try autoregressive RNN model
    i = Input(shape=(T, 1))
    x = LSTM(5)(i)
    x = Dense(1)(x)
    model = Model(i, x)
    model.compile(
        loss='mse',
        optimizer=Adam(lr=0.1),
    )

    # train the RNN
    r = model.fit(
        X[:-N // 2], Y[:-N // 2],
        epochs=80,
        validation_data=(X[-N // 2:], Y[-N // 2:]),
    )


    # plt.plot(r.history['loss'], label='loss')
    # plt.plot(r.history['val_loss'], label='val_loss')
    # plt.legend()

    # One-step forecast using true targets
    outputs = model.predict(X)
    print(outputs.shape)
    predictions = outputs[:, 0]

    # plt.plot(Y, label='targets')
    # plt.plot(predictions, label='predictions')
    # plt.legend()
    # plt.show()

    # Multi-step forecast
    validation_target = Y[-N // 2:]
    validation_predictions = []

    # first validation input
    last_x = X[-N // 2]  # 1-D array of length T

    while len(validation_predictions) < len(validation_target):
        p = model.predict(last_x.reshape(1, T, 1))[0, 0]  # 1x1 array -> scalar

        # update the predictions list
        validation_predictions.append(p)

        # make the new input
        last_x = np.roll(last_x, -1)
        last_x[-1] = p

    # plt.plot(validation_target, label='forecast target')
    # plt.plot(validation_predictions, label='forecast prediction')
    # plt.legend()

    # calculate returns by first shifting the data
    df['PrevClose'] = df['close'].shift(1)  # move everything up 1

    # so now it's like
    # close / prev close
    # x[2] x[1]
    # x[3] x[2]
    # x[4] x[3]
    # ...
    # x[t] x[t-1]

    df.head()

    # then the return is
    # (x[t] - x[t-1]) / x[t-1]
    df['Return'] = (df['close'] - df['PrevClose']) / df['PrevClose']

    df.head()

    # Now let's try an LSTM to predict returns
    df['Return'].hist()

    series = df['Return'].values[1:].reshape(-1, 1)

    # Normalize the data
    # Note: I didn't think about where the true boundary is, this is just approx.
    scaler = StandardScaler()
    scaler.fit(series[:len(series) // 2])
    series = scaler.transform(series).flatten()

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

    X = np.array(X).reshape(-1, T, 1)  # Now the data should be N x T x D
    Y = np.array(Y)
    N = len(X)
    print("X.shape", X.shape, "Y.shape", Y.shape)

    ### try autoregressive RNN model
    i = Input(shape=(T, 1))
    x = LSTM(5)(i)
    x = Dense(1)(x)
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
    # import matplotlib.pyplot as plt

    # plt.plot(r.history['loss'], label='loss')
    # plt.plot(r.history['val_loss'], label='val_loss')
    # plt.legend()

    # One-step forecast using true targets
    outputs = model.predict(X)
    print(outputs.shape)
    predictions = outputs[:, 0]

    # plt.plot(Y, label='targets')
    # plt.plot(predictions, label='predictions')
    # plt.legend()
    # plt.show()

    # Multi-step forecast
    validation_target = Y[-N // 2:]
    validation_predictions = []

    # first validation input
    last_x = X[-N // 2]  # 1-D array of length T

    while len(validation_predictions) < len(validation_target):
        p = model.predict(last_x.reshape(1, T, 1))[0, 0]  # 1x1 array -> scalar

        # update the predictions list
        validation_predictions.append(p)

        # make the new input
        last_x = np.roll(last_x, -1)
        last_x[-1] = p

    # plt.plot(validation_target, label='forecast target')
    # plt.plot(validation_predictions, label='forecast prediction')
    # plt.legend()

    # Now turn the full data into numpy arrays

    # Not yet in the final "X" format!
    input_data = df[['open', 'high', 'low', 'close', 'volume']].values
    targets = df['Return'].values

    # Now make the actual data which will go into the neural network
    T = 10  # the number of time steps to look at to make a prediction for the next day
    D = input_data.shape[1]
    N = len(input_data) - T  # (e.g. if T=10 and you have 11 data points then you'd only have 1 sample)

    # normalize the inputs
    Ntrain = len(input_data) * 2 // 3
    scaler = StandardScaler()
    scaler.fit(input_data[:Ntrain + T - 1])
    input_data = scaler.transform(input_data)

    # Setup X_train and Y_train
    X_train = np.zeros((Ntrain, T, D))
    Y_train = np.zeros(Ntrain)

    for t in range(Ntrain):
        X_train[t, :, :] = input_data[t:t + T]
        Y_train[t] = (targets[t + T] > 0)

    # Setup X_test and Y_test
    X_test = np.zeros((N - Ntrain, T, D))
    Y_test = np.zeros(N - Ntrain)

    for u in range(N - Ntrain):
        # u counts from 0...(N - Ntrain)
        # t counts from Ntrain...N
        t = u + Ntrain
        X_test[u, :, :] = input_data[t:t + T]
        Y_test[u] = (targets[t + T] > 0)

    # make the RNN
    i = Input(shape=(T, D))
    x = LSTM(50)(i)
    x = Dense(1, activation='sigmoid')(x)
    model = Model(i, x)
    model.compile(
        loss='binary_crossentropy',
        optimizer=Adam(lr=0.001),
        metrics=['accuracy'],
    )

    # train the RNN
    r = model.fit(
        X_train, Y_train,
        batch_size=32,
        epochs=300,
        validation_data=(X_test, Y_test),
    )

    model.save_weights('./my_model')


    print('DONE SONS')
    # plot the loss
    # plt.plot(r.history['loss'], label='loss')
    # plt.plot(r.history['val_loss'], label='val_loss')
    # plt.legend()
    # plt.show()

    # Plot accuracy per iteration
    # plt.plot(r.history['accuracy'], label='accuracy')
    # plt.plot(r.history['val_accuracy'], label='val_accuracy')
    # plt.legend()
    # plt.show()
