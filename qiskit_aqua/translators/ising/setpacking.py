# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import logging
from collections import OrderedDict

import numpy as np

from qiskit.quantum_info import Pauli
from qiskit_aqua import Operator

logger = logging.getLogger(__name__)


def random_number_list(n, weight_range=100, savefile=None):
    """Generate a set of positive integers within the given range.

    Args:
        n (int): size of the set of numbers.
        weight_range (int): maximum absolute value of the numbers.
        savefile (str or None): write numbers to this file.

    Returns:
        numpy.ndarray: the list of integer numbers.
    """
    number_list = np.random.randint(low=1, high=(weight_range+1), size=n)
    if savefile:
        with open(savefile, 'w') as outfile:
            for i in range(n):
                outfile.write('{}\n'.format(number_list[i]))
    return number_list


def get_setpacking_qubitops(list_of_subsets):
    """Construct the Hamiltonian for the set packing
    Args:
        list_of_subsets: list of lists (i.e., subsets)

    Returns:
        operator.Operator, float: operator for the Hamiltonian and a
        constant shift for the obj function.

    find the maximal number of subsets which are disjoint pairwise.

    Hamiltonian:
    H = A Ha + B Hb
    Ha = sum_{Si and Sj overlaps}{XiXj}
    Hb = -sum_{i}{Xi}

    Ha is to ensure the disjoint condition, while Hb is to achieve the maximal number.
    Ha is hard constraint that must be satisified. Therefore A >> B.
    In the following, we set A=10 and B = 1

    Note Xi = (Zi + 1)/2
    """
    shift = 0
    pauli_list = []
    A = 10
    n = len(list_of_subsets)
    for i in range(n):
        for j in range(i):
            if set(list_of_subsets[i]) & set(list_of_subsets[j]):
                wp = np.zeros(n)
                vp = np.zeros(n)
                vp[i] = 1
                vp[j] = 1
                pauli_list.append([A*0.25, Pauli(vp, wp)])

                vp2 = np.zeros(n)
                vp2[i] = 1
                pauli_list.append([A*0.25, Pauli(vp2, wp)])

                vp3 = np.zeros(n)
                vp3[j] = 1
                pauli_list.append([A*0.25, Pauli(vp3, wp)])

                shift += A*0.25

    for i in range(n):
        wp = np.zeros(n)
        vp = np.zeros(n)
        vp[i] = 1
        pauli_list.append([-0.5, Pauli(vp, wp)])
        shift += -0.5

    return Operator(paulis=pauli_list), shift


def read_numbers_from_file(filename):
    """Read numbers from a file

    Args:
        filename (str): name of the file.

    Returns:
        numpy.ndarray: list of numbers as a numpy.ndarray.
    """
    numbers = []
    with open(filename) as infile:
        for line in infile:
            assert(int(round(float(line))) == float(line))
            numbers.append(int(round(float(line))))
    return np.array(numbers)


def sample_most_likely(n, state_vector):
    """Compute the most likely binary string from state vector.

    Args:
        n (int): number of  qubits.
        state_vector (numpy.ndarray or dict): state vector or counts.

    Returns:
        numpy.ndarray: binary string as numpy.ndarray of ints.
    """
    if isinstance(state_vector, dict) or isinstance(state_vector, OrderedDict):
        temp_vec = np.zeros(2**n)
        total = 0
        for i in range(2**n):
            state = np.binary_repr(i, n)
            count = state_vector.get(state, 0)
            temp_vec[i] = count
            total += count
        state_vector = temp_vec / float(total)

    k = np.argmax(np.abs(state_vector))
    x = np.zeros(n)
    for i in range(n):
        x[i] = k % 2
        k >>= 1
    return x


def get_solution(x):
    """

    Args:
        x (numpy.ndarray) : binary string as numpy array.

    Returns:
        numpy.ndarray: graph solution as binary numpy array.
    """
    return 1 - x


def check_disjoint(sol, list_of_subsets):
    n = len(list_of_subsets)
    selected_subsets = []
    for i in range(n):
        if sol[i] == 1:
            selected_subsets.append(list_of_subsets[i])
    tmplen = len(selected_subsets)
    for i in range(tmplen):
        for j in range(i):
            L = selected_subsets[i]
            R = selected_subsets[j]
            if set(L) & set(R):
                return False

    return True
