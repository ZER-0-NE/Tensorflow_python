import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from mnist import MNIST
import keras

data = MNIST()

#conv1
filter_size1 = 5
num_filters1 = 16

#conv2
filter_size2 = 5
num_filters2 = 26

#fully-connected
fc_size = 128

img_size = data.img_size
img_size_flat = data.img_size_flat #1-D array of data values
img_shape = data.img_shape
num_classes = data.num_classes
num_channels = data.num_channels #no. of color channels for images

def plot_images(images, cls_true, cls_pred = None):
	assert len(images) == len(cls_true) == 9
	fig, axes = plt.subplots(3,3)
	fig.subplots_adjust(hspace = 0.3, wspace = 0.3)

	for x, y in enumerate(axes.flat):
		y.imshow(images[x].reshape(img_shape), cmap = 'binary')

		if cls_pred is None:
			xlabel = "True {0}".format(cls_true[x])
		else:
			xlabel = "True {0}, Pred: {1}".format(cls_true[x], cls_pred[x])

		y.set_xlabel(xlabel)

		y.set_xticks([])
		y.set_yticks([])

	plt.show()

images = data.x_test[0:9]
cls_true = data.y_test_cls[0:9]
plot_images(images = images, cls_true = cls_true)

def new_weights(shape):
	return tf.Variable(tf.truncated_normal(shape, stddev = 0.05))
def new_biases(length):
	return tf.Variable(tf.constant(0.05, shape = [length]))

def new_conv_layer(input, #previous layer input
					num_input_channels, #of previous layer
					filter_size, #width and height of each filter
					num_filters,
					use_pooling=True) #2x2 max-pooling
	
	shape = [filter_size, filter_size, num_input_channels, num_filters] #shape of filter-weights for convolution
	weights = new_weights(shape = shape)
	biases = new_biases(length = num_filters)

	'''
	The strides are set as 1 in all dimensions, first and last stride are labelled as 1
	first being for image-number and last for input-channel. padding =same => size of
	input and output image are same.
	'''
	layer = tf.nn.conv2d(input = input,
							filter = weights,
							strides = [1,1,1,1],
							padding = 'SAME')
	layer += biases
	if use_pooling:
		layer = tf.nn.max_pool(value = layer,
								ksize  = [1,2,2,1],
								strides = [1,2,2,1],
								padding = 'SAME')
	# ReLu calculates max(x,0) for every pixel value x in I/P img.
	layer = tf.nn.relu(layer)

	return layer, weights

def flatten_layer(layer):
	layer_shape = layer.get_shape()
	'''
	shape of input layer is assumed to be [num_images, img_width, img_height, num_channels]
	no. of features is img_width*img_height*num_channels
	we can use a function from tensorflow to calculate this
	'''
	num_features = layer_shape[1:4].num_elements()
	'''
	reshape the layer to [num_images, num_features]
	we set the size of second dimension to num_features and first dimension to 
	-1. 
	'''
	layer_flat = tf.reshape(layer, [-1, num_features])
	#the shape of flattened layer is now [num_images, img_height*img_width*num_channels]

	return layer_flat, num_features

def new_fc_layer(input, # previous layer
				num_inputs, #of prev layer
				num_outputs,
				use_relu = True)
	weights = new_weights(shape = [num_inputs,  num_outputs])
	biases = new_biases(length = num_outputs)

	layer = tf.matmul(input, weights) + biases
	if use_relu:
		layer = tf.nn.relu(layer)

	return layer

x = tf.placeholder(tf.float32, shape = [None, img_size_flat], name = 'x')
x_image = tf.reshape(x, [-1, img_size, img_size, num_channels])
y_true = tf.placeholder(tf.float32, shape = [None, num_classes], name = 'y_true')
y_true_cls = tf.argmax(y_true, axis = 1)

#Conv layer 1
layer_conv1, weights_conv1 = new_conv_layer(
							input = x_image,
							num_input_channels = num_channels,
							filter_size = filter_size1,
							num_filters = num_filters1,
							use_pooling = True)

layer_conv2, weights_conv2 = new_conv_layer(
							input = layer_conv1,
							num_input_channels = num_filters1,
							filter_size = filter_size2,
							num_filters = num_filters2,
							use_pooling = True)

#Flattening
layer_flat, num_features = flatten_layer(layer_conv2)

#FC layer
layer_fc2 = new_fc_layer(
						input = layer_fc1,
						num_inputs = fc_size,
						num_outputs = num_classes,
						use_relu = False)

