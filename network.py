import tensorflow as tf
import tflearn


def get_net(train_x, train_y):
    tf.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(train_x[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    return tflearn.regression(net)


def get_model(train_x, train_y):
    model = tflearn.DNN(get_net(train_x, train_y), tensorboard_dir='./model/tflearn_logs')
    return model
