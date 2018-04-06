#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# author: Laurent Vermue
# author_email: lauve@dtu.dk
#

import numpy as np
from scipy.stats import ortho_group


def get_data(num_of_samples = 11, params_block_one = 4, params_block_two = 4, params_block_three = 3, \
             num_of_variables_main_lin_comb = 9, num_of_batches = 1):
    """This function creates a dataset with three X-blocks, which are completely orthogonal
    amongst each other and one Y-block, that has two response variables, which are a linear combination of
    the variables defined for the three blocks.

    Parameters:
    --------------
    num_of_samples: Amount of samples for the dataset
    params_block_one: Number of variables in the first block
    params_block_two: Number of variables in the second block
    params_block_three: Number of variables in the third block
    num_of_variables_main_lin_comb: Number of variables that are randon linear combinations of each variable (Multi-Colliniearity)
    num_of_batches: Number of batches for each block (third dimension)

    Output:
    --------------
    X_1 = First X-block - Dimensionality ( num_of_samples, params_block_one*(num_of_variables_main_lin_comb+1), num_of_batches)
    X_2 = Second X-block - Dimensionality ( num_of_samples, params_block_two*(num_of_variables_main_lin_comb+1), num_of_batches)
    X_3 = Third X-block - Dimensionality ( num_of_samples, params_block_three*(num_of_variables_main_lin_comb+1), num_of_batches)
    Y = Y-block - Dimensionality (num_of_samples, 2, num_of_batches)
    """
    # TODO: X = y * weight_vector

    total_params = params_block_one + params_block_three + params_block_two

    assert num_of_samples >= total_params, "The amount of samples has to be equal \
    or higher than the amount of total parameters"


    # Parameters for Y block one
    ''' Constructing two different vectors that are
    linear combinations of the main orthogonal variables'''
    lin_vec_1 = np.arange(0, total_params * 0.1, 0.1)
    temp_vec = lin_vec_1[0:8]
    temp_vec[0] = 2
    temp_vec = temp_vec / np.linalg.norm(temp_vec)
    np.linalg.norm(temp_vec[0:4]) ** 2
    np.linalg.norm(temp_vec[4:9]) ** 2
    lin_vec_1[0:8] = temp_vec
    lin_vec_2 = np.arange(total_params * 0.1 - 0.1, -0.1, -0.1)

    # Constructing X blocks

    ## X1
    if num_of_batches == 1:
        X = np.dstack(ortho_group.rvs(num_of_samples, num_of_batches)).transpose((0, 2, 1))[:, :, 0:total_params]
    else:
        X = ortho_group.rvs(num_of_samples, num_of_batches).transpose((0,2,1))[:, :, 0:total_params]

    X_1 = X[:, :, 0:params_block_one]
    # Adding linear combinations
    rand_linear_factors = np.random.rand(num_of_variables_main_lin_comb)
    X_1_linear_comb = np.einsum('ijk,l->ijkl', X_1, rand_linear_factors).reshape((num_of_batches, num_of_samples, -1))
    X_1_complete = np.concatenate((X_1, X_1_linear_comb), -1)

    ## X2
    X_2 = X[:, :, params_block_one:params_block_one+params_block_two]
    # Adding linear combinations
    rand_linear_factors = np.random.rand(num_of_variables_main_lin_comb)
    X_2_linear_comb = np.einsum('ijk,l->ijkl', X_2, rand_linear_factors).reshape((num_of_batches, num_of_samples, -1))
    X_2_complete = np.concatenate((X_2, X_2_linear_comb), -1)

    ## X3
    X_3 = X[:, :, params_block_one+params_block_two:total_params]
    # Adding linear combinations
    rand_linear_factors = np.random.rand(num_of_variables_main_lin_comb)
    X_3_linear_comb = np.einsum('ijk,l->ijkl', X_3, rand_linear_factors).reshape((num_of_batches, num_of_samples, -1))
    X_3_complete = np.concatenate((X_3, X_3_linear_comb), -1)

    # Constructing Y block
    y1 = np.einsum('j,klj->kl', lin_vec_1, X[:, :, 0:total_params])
    y2 = np.einsum('j,klj->kl', lin_vec_2, X[:, :, 0:total_params])
    Y = np.stack((y1, y2), -1)
    if num_of_batches == 1:
        return np.squeeze(X_1_complete), np.squeeze(X_2_complete), np.squeeze(X_3_complete), np.squeeze(Y)
    else:
        return X_1_complete, X_2_complete, X_3_complete, Y