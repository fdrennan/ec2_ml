from tensorflow.keras.layers import Input, Dense, Flatten, Conv1D, AveragePooling1D, concatenate
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import plot_model
import pandas as pd
import numpy as np
from tensorflow.keras import optimizers
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# https://www.coursera.org/learn/customising-models-tensorflow2/lecture/84LZF/the-keras-functional-api
if __name__ == '__main__':
    model_data_url = 'https://raw.githubusercontent.com/phgbecker/acute-inflammations-classifier/master/acute-inflammations.csv'

    model_data = pd.read_csv(model_data_url)

    # Model Specific Cleaning Required
    categorical_data = model_data.select_dtypes('object')
    numeric_data = model_data.select_dtypes('float64')
    categorical_data = categorical_data.apply(lambda value: value == 'yes').astype(int)
    model_data = pd.concat([numeric_data.reset_index(drop=True), categorical_data], axis=1).values

    # Split Train and Test
    X_train, X_test, Y_train, Y_test = train_test_split(model_data[:, :6],
                                                        model_data[:, 6:],
                                                        test_size=0.33)

    temp_train, nocc_train, lumbp_train, up_train, mict_train, bis_train = np.transpose(X_train)
    temp_test, nocc_test, lumbp_test, up_test, mict_test, bis_test = np.transpose(X_test)

    inflam_train, nephr_train = Y_train[:, 0], Y_train[:, 1]
    inflam_test, nephr_test = Y_test[:, 0], Y_test[:, 1]

    # Build The Model
    shape_inputs = (1,)
    temperature = Input(shape=shape_inputs, name='temp')
    nausea_occurrence = Input(shape=shape_inputs, name='nocc')
    lumbar_pain = Input(shape=shape_inputs, name='lumbp')
    urine_pushing = Input(shape=shape_inputs, name='up')
    micturition_pains = Input(shape=shape_inputs, name='mict')
    bis = Input(shape=shape_inputs, name='bis')

    # Create a list of all the inputs
    list_inputs = [temperature, nausea_occurrence, lumbar_pain, urine_pushing, micturition_pains, bis]

    # Merge all input features into a single large vector
    x = concatenate(list_inputs)

    # Use a logistic regression classifier for disease prediction
    inflammation_pred = Dense(1, activation='sigmoid', name='inflam')(x)
    nephritis_pred = Dense(1, activation='sigmoid', name='nephr')(x)

    # Create a list of all the outputs
    list_outputs = [inflammation_pred, nephritis_pred]
    # Create the model object
    model = Model(inputs=list_inputs, outputs=list_outputs)

    # Display the multiple input/output model
    plot_model(model, 'multi_input_output_model.png', show_shapes=True)

    # Compile the model
    model.compile(optimizer=optimizers.RMSprop(1e-3),
                  loss={'inflam': 'binary_crossentropy',
                        'nephr': 'binary_crossentropy'},
                  metrics={'inflam': ['acc'],
                           'nephr': ['acc']},
                  loss_weights=[1.0, 0.2])

    # Define training inputs and outputs
    inputs_train = {'temp': temp_train, 'nocc': nocc_train, 'lumbp': lumbp_train,
                    'up': up_train, 'mict': mict_train, 'bis': bis_train}

    outputs_train = {'inflam': inflam_train, 'nephr': nephr_train}

    # Train the model
    history = model.fit(inputs_train, outputs_train, epochs=1000, batch_size=128, verbose=True)

    # Plot the training accuracy

    acc_keys = [k for k in history.history.keys() if k in ('inflam_acc', 'nephr_acc')]
    loss_keys = [k for k in history.history.keys() if k in ('loss', 'inflam_loss', 'nephr_loss')]

    for k, v in history.history.items():
        if k in acc_keys:
            plt.figure(1)
            plt.plot(v)

    plt.figure(1)
    plt.title('Accuracy vs. epochs')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(acc_keys, loc='upper right')

    plt.show()

    for k, v in history.history.items():
        if k in loss_keys:
            plt.figure(2)
            plt.plot(v)

    plt.figure(2)
    plt.title('Loss vs. epochs')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(loss_keys, loc='upper right')
    plt.show()

    # Evaluate the model
    inputs_test = {'temp': temp_test, 'nocc': nocc_test, 'lumbp': lumbp_test,
                   'up': up_test, 'mict': mict_test, 'bis': bis_test}

    outputs_test = {'inflam': inflam_test, 'nephr': nephr_test}
    model.evaluate(inputs_test, outputs_test)

    model.save('my_model')
