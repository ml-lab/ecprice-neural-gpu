"""Various improvements to the tensorflow API."""
import tensorflow as tf
from tensorflow.python.training import moving_averages
import functools

def shape_list(tensor):
  """Return the tensor shape in a form tf.reshape understands."""
  return [x or -1 for x in tensor.get_shape().as_list()]

def safe_squeeze(array, i):
  shape = shape_list(array)
  assert shape[i] == 1
  return tf.reshape(array, shape[:i] + (shape[i+1:] if (i+1) else []))

def expand_dims_by_k(array, k):
  return tf.reshape(array, shape_list(array) + [1]*k)


def fix_batching(f, k, nargs=1):
  """Make a given function f support extra initial dimensions.

  A number of tf.nn operations expect shapes of the form [-1] + lst
  where len(lst) is a fixed constant, and operate independently on the
  -1.  This lets them work on shapes of the form lst2 + lst, where
  lst2 is arbitrary.

  args:
    k: len(lst) that f wants
    nargs: Number of tensors with this property
  """
  @functools.wraps(f)
  def wrapper(*args, **kws):
    arrays = args[:nargs]
    old_shape = shape_list(arrays[0])
    used_shape = old_shape[-k:]
    inputs_reshaped = tuple(tf.reshape(array, [-1]+used_shape)
                       for array in arrays)
    output = f(*(inputs_reshaped + args[nargs:]), **kws)
    new_prefix = old_shape[:-k]
    new_suffix = shape_list(output)[1:]
    output_reshaped = tf.reshape(output, new_prefix + new_suffix)
    return output_reshaped
  return wrapper

softmax = fix_batching(tf.nn.softmax, 1)
conv2d = fix_batching(tf.nn.conv2d, 3)
softmax_cross_entropy_with_logits = fix_batching(tf.nn.softmax_cross_entropy_with_logits, 1, 2)




# From http://stackoverflow.com/questions/33949786/how-could-i-use-batch-normalization-in-tensorflow
# and https://github.com/ry/tensorflow-resnet/blob/master/resnet.py
def batch_norm(x, phase_train, scope='bn'):
    """
    Batch normalization on convolutional maps.
    Args:
        x:           Tensor, 4D BHWD input maps
        n_out:       integer, depth of input maps
        phase_train: boolean tf.Varialbe, true indicates training phase
        scope:       string, variable scope
    Return:
        normed:      batch-normalized maps
    """
    x_shape = shape_list(x)
    params_shape = x_shape[-1:]
    BN_DECAY = 0.8
    BN_EPSILON = 1e-3
    with tf.variable_scope(scope) as vs:
        beta = tf.get_variable('beta', params_shape, initializer=tf.zeros_initializer)
        gamma = tf.get_variable('gamma', params_shape, initializer=tf.ones_initializer)
        moving_mean = tf.get_variable('moving_mean', params_shape,
                                      initializer=tf.zeros_initializer, trainable=False)
        moving_var = tf.get_variable('moving_var', params_shape,
                                     initializer=tf.ones_initializer, trainable=False)
        axes = range(len(x_shape)-1)
        batch_mean, batch_var = tf.nn.moments(x, axes, name='moments')

        update_ops = [
            moving_averages.assign_moving_average(moving_mean, batch_mean, BN_DECAY),
            moving_averages.assign_moving_average(moving_var, batch_var, BN_DECAY)]
        def mean_var_with_update():
            with tf.control_dependencies(update_ops):
                return tf.identity(batch_mean), tf.identity(batch_var)

        mean, var = tf.cond(phase_train,
                            mean_var_with_update,
                            lambda: (moving_mean, moving_var))
        normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, BN_EPSILON)
    return normed


