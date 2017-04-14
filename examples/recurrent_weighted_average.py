import numpy as np
from recurrentshop import RecurrentModel
from keras.models import Model
from keras.layers import Dense, Activation, Lambda, Input
from keras.layers import add, concatenate, multiply
from keras import backend as K
from keras import initializers


def generate_data(num_samples, max_len):
    data = np.zeros([num_samples, max_len])
    labels = np.zeros([num_samples, 1])

    for sample, label in zip(data, labels):
        length = np.random.randint(1, max_len+1)
        n = np.random.normal()
        sample[:length] += n
        if length > max_len/2:
            label += 1

    data = np.expand_dims(data, axis=-1)
    return data, labels


def RWA(input_dim, output_dim):
    x = Input((input_dim, ))
    h_tm1 = Input((output_dim, ))
    n_tm1 = Input((output_dim, ))
    d_tm1 = Input((output_dim, ))

    x_h = concatenate([x, h_tm1])

    u = Dense(output_dim)(x)
    g = Dense(output_dim, activation='tanh')(x_h)

    a = Dense(output_dim, use_bias=False)(x_h)
    e_a = Lambda(lambda x: K.exp(x))(a)

    z = multiply([u, g])
    nt = add([n_tm1, multiply([z, e_a])])
    dt = add([d_tm1, e_a])
    dt = Lambda(lambda x: 1.0/x)(dt)
    ht = multiply([nt, dt])
    ht = Activation('tanh')(ht)

    return RecurrentModel(input=x, output=ht,
                          initial_states=[h_tm1, n_tm1, d_tm1],
                          final_states=[ht, nt, dt],
                          state_initializer=[initializers.random_normal(stddev=1.0)])


input_dim = 1
output_dim = 250
timesteps = 100
batch_size = 100
n_epochs = 10
train_data, train_labels = generate_data(num_samples=100000, max_len=timesteps)
test_data, test_labels = generate_data(num_samples=10000, max_len=timesteps)

rwa = RWA(input_dim, output_dim)

inp = Input((timesteps, input_dim))
out = rwa(inp)
out = Dense(1, activation='sigmoid')(out)
model = Model(inp, out)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(train_data, train_labels, batch_size=batch_size, epochs=n_epochs)
model.evaluate(test_data, test_labels, batch_size=batch_size)