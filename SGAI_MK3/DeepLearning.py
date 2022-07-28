import numpy as np
import tensorflow as tf         #pip install tensorflow
from tensorflow import keras
import keras.layers as layers

def create_q_model(rows, columns, num_actions):
    # Network defined by the Deepmind paper
    inputs = layers.Input(shape=(columns, rows, 1))
    
    # Convolutions on the frames on the screen
    layer1 = layers.Conv2D(filters=10, kernel_size=(3,3), activation="relu")(inputs)
    layer2 = layers.Conv2D(64, 4, strides=2, activation="relu")(layer1)
    layer3 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer2)
    layer4 = layers.Flatten()(layer3)
    layer5 = layers.Dense(512, activation="relu")(layer4)
    action = layers.Dense(num_actions, activation="linear")(layer5)
    
    return keras.Model(inputs=inputs, outputs=action)