from __future__ import absolute_import, division, print_function, unicode_literals

import pandas as pd
import numpy as np
import math
import tensorflow as tf

from tensorflow.keras import layers
from sklearn.model_selection import train_test_split

X = pd.read_pickle('2014_mpg15_g30_playerlist_data')
y = X.pop('target')


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.10, stratify = y)
X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train, test_size=0.277777, stratify = y_train)
num_train_examples = len(y_train)
num_val_examples = len(y_validation)
num_test_examples = len(y_test)

train = pd.DataFrame(np.hstack((np.asarray(X_train), np.reshape(np.asarray(y_train),(-1,1))  )))
val = pd.DataFrame(np.hstack((np.asarray(X_validation), np.reshape(np.asarray(y_validation),(-1,1)))))
test = pd.DataFrame(np.hstack((np.asarray(X_test), np.reshape(np.asarray(y_test),(-1,1)) )))

train_dataset = tf.data.Dataset.from_tensor_slices((
         tf.cast(train[train.columns[:-1]].values, tf.float32),
         tf.cast(train[train.columns[-1]].values, tf.int32)))
validation_dataset = tf.data.Dataset.from_tensor_slices((
         tf.cast(val[val.columns[:-1]].values, tf.float32),
         tf.cast(val[val.columns[-1]].values, tf.int32)))
test_dataset = tf.data.Dataset.from_tensor_slices((
         tf.cast(test[test.columns[:-1]].values, tf.float32),
         tf.cast(test[test.columns[-1]].values, tf.int32)))

model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(26, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

BATCH_SIZE = 10
train_dataset = train_dataset.cache().repeat().shuffle(num_train_examples).batch(BATCH_SIZE)
validation_dataset = validation_dataset.cache().batch(BATCH_SIZE)

model.fit(train_dataset, epochs=5, steps_per_epoch=math.ceil(num_train_examples/BATCH_SIZE))
test_loss, test_accuracy = model.evaluate(validation_dataset, steps=math.ceil(num_val_examples/BATCH_SIZE))
print('Accuracy on validation dataset:', test_accuracy)
