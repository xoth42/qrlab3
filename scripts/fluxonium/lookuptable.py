import numpy as np
from numpy import matmul as mul
from numpy.linalg import inv as inv
from numpy.linalg import eig as eig
from numpy import tensordot as tensor
from numpy import dot

import pickle

#import TwoQ_RB

def CheckIdentity(matrix):
    """
    Check whether the matrix is identity by calculating it numerically.

    Parameters
    ----------
    matrix: 4x4 np.matrix
        matrix

    Returns
    -------
    result: bool
        True, if identity.
    """

    #Check all the diagonal entries.
#    if ((np.abs(matrix[0,0]-1)< 1e-6) and
#        (np.abs(matrix[1,1]-1)< 1e-6) and
#        (np.abs(matrix[2,2]-1)< 1e-6) and
#        (np.abs(matrix[3,3]-1)< 1e-6)):
    if ((np.abs(np.abs(matrix[0,0])-1)< 1e-3) and
        (np.abs(np.abs(matrix[1,1])-1)< 1e-3) and
        (np.abs(np.abs(matrix[2,2])-1)< 1e-3) and
        (np.abs(np.abs(matrix[3,3])-1)< 1e-3) and
        (np.abs(matrix[1,1]/matrix[0,0]-1)<1e-3) and
        (np.abs(matrix[2,2]/matrix[0,0]-1)<1e-3) and
        (np.abs(matrix[3,3]/matrix[0,0]-1)<1e-3)):
        return True
    else:
        return False

def evaluate_sequence(gate_seq_1, gate_seq_2, generator):
        """
        Evaluate the two qubit gate sequence.

        Parameters
        ----------
        gate_seq_1: list of class Gate (defined in "gates.py")
            The gate sequence applied to Qubit "1"

        gate_seq_2: list of class Gate (defined in "gates.py")
            The gate sequence applied to Qubit "2"

        Returns
        -------
        twoQ_gate: np.matrix (shape = (4,4))
            The evaulation result.
        """
        
        twoQ_gate = np.matrix(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        for i in range(len(gate_seq_1)):
                
            gate_1 = np.matrix([[1, 0], [0, 1]])
            gate_2 = np.matrix([[1, 0], [0, 1]])
            if (gate_seq_1[i] == 'I'):
                pass
            elif (gate_seq_1[i] == 'X2p'):
                gate_1 = np.matmul(
                    np.matrix([[1, -1j], [-1j, 1]]) / np.sqrt(2), gate_1)
            elif (gate_seq_1[i] == 'X2m'):
                gate_1 = np.matmul(
                    np.matrix([[1, 1j], [1j, 1]]) / np.sqrt(2), gate_1)
            elif (gate_seq_1[i] == 'Y2p'):
                gate_1 = np.matmul(
                    np.matrix([[1, -1], [1, 1]]) / np.sqrt(2), gate_1)
            elif (gate_seq_1[i] == 'Y2m'):
                gate_1 = np.matmul(
                    np.matrix([[1, 1], [-1, 1]]) / np.sqrt(2), gate_1)
            elif (gate_seq_1[i] == 'Xp'):
                gate_1 = np.matmul(np.matrix([[0, -1j], [-1j, 0]]), gate_1)
            elif (gate_seq_1[i] == 'Xpm'):
                gate_1 = np.matmul(np.matrix([[0, 1j], [1j, 0]]), gate_1)
            elif (gate_seq_1[i] == 'Yp'):
                gate_1 = np.matmul(np.matrix([[0, -1], [1, 0]]), gate_1)
            elif (gate_seq_1[i] == 'Ypm'):
                gate_1 = np.matmul(np.matrix([[0, 1], [-1, 0]]), gate_1)
            elif (gate_seq_1[i] == 'Z2p'):
                gate_1 = np.matmul(np.matrix([[1+1j, 0], [0, 1-1j]]) / np.sqrt(2), gate_1)
            elif (gate_seq_1[i] == 'Z2m'):
                gate_1 = np.matmul(np.matrix([[1-1j, 0], [0, 1+1j]]) / np.sqrt(2), gate_1)

            if (gate_seq_2[i] == 'I'):
                pass
            elif (gate_seq_2[i] == 'X2p'):
                gate_2 = np.matmul(
                    np.matrix([[1, -1j], [-1j, 1]]) / np.sqrt(2), gate_2)
            elif (gate_seq_2[i] == 'X2m'):
                gate_2 = np.matmul(
                    np.matrix([[1, 1j], [1j, 1]]) / np.sqrt(2), gate_2)
            elif (gate_seq_2[i] == 'Y2p'):
                gate_2 = np.matmul(
                    np.matrix([[1, -1], [1, 1]]) / np.sqrt(2), gate_2)
            elif (gate_seq_2[i] == 'Y2m'):
                gate_2 = np.matmul(
                    np.matrix([[1, 1], [-1, 1]]) / np.sqrt(2), gate_2)
            elif (gate_seq_2[i] == 'Xp'):
                gate_2 = np.matmul(np.matrix([[0, -1j], [-1j, 0]]), gate_2)
            elif (gate_seq_2[i] == 'Xpm'):
                gate_2 = np.matmul(np.matrix([[0, 1j], [1j, 0]]), gate_2)
            elif (gate_seq_2[i] == 'Yp'):
                gate_2 = np.matmul(np.matrix([[0, -1], [1, 0]]), gate_2)
            elif (gate_seq_2[i] == 'Ypm'):
                gate_2 = np.matmul(np.matrix([[0, 1], [-1, 0]]), gate_2)
            elif (gate_seq_2[i] == 'Z2p'):
                gate_2 = np.matmul(np.matrix([[1+1j, 0], [0, 1-1j]]) / np.sqrt(2), gate_2)
            elif (gate_seq_2[i] == 'Z2m'):
                gate_2 = np.matmul(np.matrix([[1-1j, 0], [0, 1+1j]]) / np.sqrt(2), gate_2)

            gate_12 = np.kron(gate_1, gate_2)
            
            if generator == 'CNOT':
                if (gate_seq_1[i] == 'CNOT' or gate_seq_2[i] == 'CNOT'):
                    gate_12 = np.matmul(
                            np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1],
                                       [0, 0, 1, 0]]), gate_12)
            elif generator == 'ZX90':
                if (gate_seq_1[i] == 'ZX90' or gate_seq_2[i] == 'ZX90'):
                    gate_12 = np.matmul(
                            np.matrix([[1, -1j, 0, 0], [-1j, 1, 0, 0], [0, 0, 1, 1j],
                                       [0, 0, 1j, 1]]) / np.sqrt(2), gate_12)
            elif generator == 'CX':
                if (gate_seq_1[i] == 'CX' or gate_seq_2[i] == 'CX'):
                    gate_12 = np.matmul(
                            np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -1j],
                                       [0, 0, -1j, 0]]), gate_12)
            elif generator == 'CZ':
                if (gate_seq_1[i] == 'CZ' or gate_seq_2[i] == 'CZ'):
                    gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
                                   [0, 0, 0, -1]]), gate_12)
            elif generator == 'iSWAP':
                if (gate_seq_1[i] == 'iSWAP' or gate_seq_2[i] == 'iSWAP'):
                    gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 0, 1j, 0], [0, 1j, 0, 0],
                                   [0, 0, 0, 1]]), gate_12)
            elif generator == 'u':
                if (gate_seq_1[i] == 'u' or gate_seq_2[i] == 'u'):
                    gate_12 = np.matmul(
                        np.matrix([[1, 0, 0, 0], [0, 2, 0, 0], [0, 0, 3, 0],
                                   [0, 0, 0, 4]]), gate_12)
            twoQ_gate = np.matmul(gate_12, twoQ_gate)
        return twoQ_gate
    
def add_singleQ_clifford(index, gate_seq, **kwargs):
        """Add single qubit clifford (24)."""
        
        length_before = len(gate_seq)
        # Paulis
        if index == 0:
            gate_seq.append('I')
            
            
        elif index == 1:
            
            gate_seq.append('Xp')
            
        elif index == 2:
            
            gate_seq.append('Yp')
            
        elif index == 3:
            
            
            gate_seq.append('Yp')
            gate_seq.append('Xp')
            
    
        # 2pi/3 rotations
        elif index == 4:
            
            
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            
        elif index == 5:
            
            
            gate_seq.append('X2p')
            gate_seq.append('Y2m')
            
        elif index == 6:
            
            
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            
        elif index == 7:
            
            
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            
        elif index == 8:
            
            
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            
        elif index == 9:
            
            
            gate_seq.append('Y2p')
            gate_seq.append('X2m')
            
        elif index == 10:
            
            
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            
        elif index == 11:
            
            
            gate_seq.append('Y2m')
            gate_seq.append('X2m')
            
    
        # pi/2 rotations
        elif index == 12:
            
            gate_seq.append('X2p')
            
        elif index == 13:
            
            gate_seq.append('X2m')
            
        elif index == 14:
            
            gate_seq.append('Y2p')
            
        elif index == 15:
            
            gate_seq.append('Y2m')
            
        elif index == 16:
            
            
            
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            
        elif index == 17:
            
            
            
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')
            
    
        # Hadamard-Like
        elif index == 18:
            
            
            gate_seq.append('Xp')
            gate_seq.append('Y2p')
            
        elif index == 19:
            
            
            gate_seq.append('Xp')
            gate_seq.append('Y2m')
            
        elif index == 20:
            
            
            gate_seq.append('Yp')
            gate_seq.append('X2p')
            
        elif index == 21:
            
            
            gate_seq.append('Yp')
            gate_seq.append('X2m')
            
        elif index == 22:
            
            
            
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            
        elif index == 23:
            
            
            
            gate_seq.append('X2m')
            gate_seq.append('Y2p')
            gate_seq.append('X2m')
            
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 24 and greater'
                ' or equal to 0: ', str(index))
        length_after = len(gate_seq)
        for i in range(3-(length_after-length_before)):
                gate_seq.append('I')
                
def add_singleQ_clifford_virtualZ(index, gate_seq, **kwargs):
        """Add single qubit clifford using virtual Z gates (24)."""
        
        length_before = len(gate_seq)
        # Paulis
        if index == 0:
            gate_seq.append('I')

        elif index == 1:
            gate_seq.append('Xp')

        elif index == 2:
            gate_seq.append('Z2p')
            gate_seq.append('Xp')
            gate_seq.append('Z2m')
        elif index == 3:
            gate_seq.append('Zp')
    
        # 2pi/3 rotations
        elif index == 4:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            
        elif index == 5:

            gate_seq.append('X2p')
            gate_seq.append('Z2p')
            gate_seq.append('X2m')
            gate_seq.append('Z2m')
        elif index == 6:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            gate_seq.append('Zp')

        elif index == 7:

            gate_seq.append('X2m')
            gate_seq.append('Z2p')
            gate_seq.append('X2m')
            gate_seq.append('Z2m')
        elif index == 8:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            gate_seq.append('Z2m')
            gate_seq.append('X2p')
        elif index == 9:
            gate_seq.append('X2m')
            gate_seq.append('Z2p')
        elif index == 10:
            gate_seq.append('Zp')
            gate_seq.append('X2m')
            gate_seq.append('Z2m')

        elif index == 11:
            gate_seq.append('X2m')
            gate_seq.append('Z2m')

    
        # pi/2 rotations
        elif index == 12:
            gate_seq.append('X2p')
        elif index == 13:
            gate_seq.append('X2m')
        elif index == 14:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            gate_seq.append('Z2m')
        elif index == 15:
            gate_seq.append('Z2p')
            gate_seq.append('X2m')
            gate_seq.append('Z2m')
        elif index == 16:
            gate_seq.append('Z2m')
        elif index == 17:
            gate_seq.append('Z2p')

    
        # Hadamard-Like
        elif index == 18:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            gate_seq.append('Z2p')

        elif index == 19:

            gate_seq.append('Xp')
            gate_seq.append('Z2p')
            gate_seq.append('X2m')
            gate_seq.append('Z2m')
        elif index == 20:

            gate_seq.append('Z2p')
            gate_seq.append('Xp')
            gate_seq.append('Z2m')
            gate_seq.append('X2p')
        elif index == 21:

            gate_seq.append('Z2p')
            gate_seq.append('Xp')
            gate_seq.append('Z2m')
            gate_seq.append('X2m')
        elif index == 22:
            gate_seq.append('Z2p')
            gate_seq.append('Xp')

        elif index == 23:
            gate_seq.append('Z2p')
            gate_seq.append('X2p')
            gate_seq.append('Zp')
            gate_seq.append('X2m')

        else:
            raise ValueError(
                'index is out of range. it should be smaller than 24 and greater'
                ' or equal to 0: ', str(index))
    
        length_after = len(gate_seq)
        # Force the clifford to have a length of 4 gates
        for i in range(4-(length_after-length_before)):
            gate_seq.append('I')

    
    
def add_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator = 'CNOT'):
        """Add single qubit clifford (11520 = 576 + 5184 + 5184 + 576)."""
        
        
        
#        print(index)
#        print(type(index))
#        
        if (index < 0):
            raise ValueError(
                'index is out of range. it should be smaller than 11520 and '
                'greater or equal to 0: ', str(index))
        elif (index < 576):
            add_singleQ_based_twoQ_clifford(index, gate_seq_1, gate_seq_2)
        elif (index < 5184 + 576):
            add_CNOT_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator = generator)
        elif (index < 5184 + 5184 + 576):
            add_iSWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator = generator)
        elif (index < 576 + 5184 + 5184 + 576):
            add_SWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator = generator)
        else:
            raise ValueError(
                'index is out of range. it should be smaller than 11520 and '
                'greater or equal to 0: ', str(index))
    
        pass
    
    
def add_singleQ_S1(index, gate_seq):
        """Add single qubit clifford from S1.
    
        (I-like-subset of single qubit clifford group) (3)
        """
      
        
        if index == 0:
            gate_seq.append('I')
            gate_seq.append('I')  # auxiliary
            gate_seq.append('I')  # auxiliary
            
#            
#            
            
        elif index == 1:
            gate_seq.append('Y2p')
            gate_seq.append('X2p')
            gate_seq.append('I')  # auxiliary
            
            
#            
            
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('I')  # auxiliary
            
            
#            
            
    
def add_singleQ_S1_X2p(index, gate_seq):
        """Add single qubit clifford from S1_X2p.
    
        (X2p-like-subset of single qubit clifford group) (3)
        """
        
        if index == 0:
            gate_seq.append('X2p')
            gate_seq.append('I')
            gate_seq.append('I')

        elif index == 1:
            gate_seq.append('X2p')
            gate_seq.append('Y2p')
            gate_seq.append('X2p')

        elif index == 2:
            gate_seq.append('Y2m')
            gate_seq.append('I')
            gate_seq.append('I')
            
def add_singleQ_S1_Y2p(index, gate_seq):
        """Add single qubit clifford from S1_Y2p.
    
        (Y2p-like-subset of single qubit clifford group) (3)
        """
        
        if index == 0:
            gate_seq.append('Y2p')
            gate_seq.append('I')
            gate_seq.append('I')
        elif index == 1:
            gate_seq.append('Yp')
            gate_seq.append('X2p')
            gate_seq.append('I')
        elif index == 2:
            gate_seq.append('X2m')
            gate_seq.append('Y2m')
            gate_seq.append('X2p')

def add_singleQ_S1_X2p_Y2m(index, gate_seq):
        """Add single qubit clifford from S1_X2p.
    
        (X2p-like-subset of single qubit clifford group) (3)
        """
        
        if index == 0:
            gate_seq.append('X2p')
            gate_seq.append('Y2m')
            gate_seq.append('I')

        elif index == 1:
            gate_seq.append('Xp')
            gate_seq.append('I')
            gate_seq.append('I')

        elif index == 2:
            gate_seq.append('Y2m')
            gate_seq.append('X2m')
            gate_seq.append('I')
            
def add_singleQ_based_twoQ_clifford(index, gate_seq_1, gate_seq_2, **kwargs):
        """Add single-qubit-gates-only-based two Qubit Clifford.
    
        (24*24 = 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        
        
#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
        add_singleQ_clifford(index_1, gate_seq_1)
        add_singleQ_clifford(index_2, gate_seq_2)
    
    
def add_CNOT_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator, **kwargs):
        """Add CNOT like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        
        
     
#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
        # randomly sample from S1 (3)
        index_3 = (index // 24 // 24) % 3
    
        # randomly sample from S1_Y2p (3) or S1_Z2p (3)
        index_4 = (index // 24 // 24 // 3) % 3
            
        if generator == 'CNOT':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')
            
            add_singleQ_S1(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
            
        elif generator == 'ZX90':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
            add_singleQ_S1(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
    
        elif generator == 'CX':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            add_singleQ_S1(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
            
        elif generator == 'CZ':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
            
            gate_seq_1.append('I')
            gate_seq_2.append('CZ')
            add_singleQ_S1(index_3, gate_seq_1)
            add_singleQ_S1_Y2p(index_4, gate_seq_2)
    
    
def add_iSWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator, **kwargs):
        """Add iSWAP like two Qubit Clifford.
    
        (24*24*3*3 = 5184)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        
        
#        print(index)
#        print(type(index))
            
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
    
        # randomly sample from S1_Y2p (3) or S1 (3)
        index_3 = (index // 24 // 24) % 3
    
        # randomly sample from S1_X2p (3) or S1 (3)
        index_4 = (index // 24 // 24 // 3) % 3
            
        if generator == 'CNOT':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
            
            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')

            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')

            
 
            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')
            
            add_singleQ_S1_X2p(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
            
        elif generator == 'ZX90':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
            gate_seq_1.append('Xpm')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('X2m')
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('I')
            
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')

            
            add_singleQ_S1_X2p(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
            
        elif generator == 'CX':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            add_singleQ_S1_X2p_Y2m(index_3, gate_seq_1)
            add_singleQ_S1(index_4, gate_seq_2)
            
        elif generator == 'CZ':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
           
            gate_seq_1.append('Y2p')
            gate_seq_2.append('X2m')
                    
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            
            add_singleQ_S1_Y2p(index_3, gate_seq_1)
            add_singleQ_S1_X2p(index_4, gate_seq_2)
    
    
def add_SWAP_like_twoQ_clifford(index, gate_seq_1, gate_seq_2, generator, **kwargs):
        """Add SWAP like two Qubit Clifford.
    
        (24*24*= 576)
        (gate_seq_1: gate seq. of qubit #1, gate_seq_t: gate seq. of qubit #2)
        """
        
        

#        print(index)
#        print(type(index))
        
        # randomly sample from single qubit cliffords (24)
        index_1 = index % 24
#        print(index_1)
#        print(type(index_1))
    
        # randomly sample from single qubit cliffords (24)
        index_2 = (index // 24) % 24
            
        if generator == 'CNOT':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
        
            
            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')

            gate_seq_1.append('Y2p')
            gate_seq_1.append('Xp')
 
            gate_seq_2.append('Y2p')
            gate_seq_2.append('Xp')

            

            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')

            
            gate_seq_1.append('Y2p')
            gate_seq_1.append('Xp')

            gate_seq_2.append('Y2p')
            gate_seq_2.append('Xp')
            

            gate_seq_1.append('I')
            gate_seq_2.append('CNOT')
            
        elif generator == 'ZX90':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
            gate_seq_1.append('Y2p')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('X2p')
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('I')
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('I')
            
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
            gate_seq_1.append('Y2p')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('X2p')
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('I')
            
            gate_seq_1.append('X2p')
            gate_seq_2.append('I')
            
            gate_seq_1.append('I')
            gate_seq_2.append('ZX90')
            
        elif generator == 'CX':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                    
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Xp')
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
            gate_seq_1.append('X2m')
            gate_seq_2.append('Y2p')
            
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Xp')
            
            gate_seq_1.append('I')
            gate_seq_2.append('CX')
            
        elif generator == 'CZ':
            add_singleQ_clifford(index_1, gate_seq_1)
            add_singleQ_clifford(index_2, gate_seq_2)
                                
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
        
            gate_seq_1.append('Y2m')
            gate_seq_2.append('Y2p')
                
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            
            gate_seq_1.append('Y2p')
            gate_seq_2.append('Y2m')
            
            gate_seq_1.append('Ic')
            gate_seq_2.append('CZ')
            
            gate_seq_1.append('Ip')
            gate_seq_2.append('Y2p')
                
    
generator = 'ZX90'
initial_state = np.matrix('1;0;0;0') # qubit starts in |gg>
num_2Q_cliffords = 11520
final_state_list = []
unique_final_state_list = []
clifford_matrix_list = []
unique_clifford_matrix_list = []
recovery_list_1 = []
recovery_list_2 = []
recovery_index_list = []
for i in range(num_2Q_cliffords):
    print(('Calculating 2Q clifford #:', i+1))
    gateseq_1 = []
    gateseq_2 = []
    add_twoQ_clifford(i, gateseq_1, gateseq_2, generator = generator)
    clifford_matrix = evaluate_sequence(gateseq_1, gateseq_2, generator = generator)

    final_state = np.asarray(np.matmul(clifford_matrix, initial_state))
    final_state_list.append(final_state)
    clifford_matrix_arr = np.asarray(clifford_matrix)
    clifford_matrix_list.append(clifford_matrix_arr)

    if i == 0:
        unique_final_state_list.append(final_state)
        unique_clifford_matrix_list.append(clifford_matrix_arr)
    else:
        if any(np.array_equal(final_state, j) for j in unique_final_state_list[:]) == True:
            print('found final state')
        else:
            print('adding new final state')
            unique_final_state_list.append(final_state)
        if any(np.array_equal(clifford_matrix_arr, k) for k in unique_clifford_matrix_list[:]) == True:
            print('found clifford matrix')
        else:
            print('adding new clifford matrix')
            unique_clifford_matrix_list.append(clifford_matrix_arr)
    print('finding recovery')        
    for m in range(num_2Q_cliffords):
        recovseq_1 = []
        recovseq_2 = []
        add_twoQ_clifford(m, recovseq_1, recovseq_2, generator = generator)
        recovery_matrix = evaluate_sequence(recovseq_1, recovseq_2, generator = generator)
        if CheckIdentity(np.matmul(recovery_matrix, clifford_matrix)):
            print('found recovery')
            recovery_list_1.append(recovseq_1)
            recovery_list_2.append(recovseq_2)
            recovery_index_list.append(m)
            break
    
    
with open('ZX90_clifford_matrix_list.pickle', 'wb') as filepath:
    pickle.dump(unique_clifford_matrix_list, filepath)
    
with open('ZX90_recovery_table.pickle', 'wb') as filepath:
    pickle.dump(recovery_index_list, filepath)
    
    
#cliff_mat_list_virtualZ = []
#for i in range(num_2Q_cliffords):
#    print('Calculating 2Q clifford(w/ virtualZ) #:', i+1)
#    gateseq_1 = []
#    gateseq_2 = []
#    add_twoQ_clifford(i, gateseq_1, gateseq_2, generator = generator)
#    clifford_matrix = evaluate_sequence(gateseq_1, gateseq_2, generator = generator)
#    cliff_mat_list_virtualZ.append(clifford_matrix)
##
'''
iSWAP_CX_seq1 = ['X2m', 'Z2p', 'I', 'X2m', 'I', 'X2p', 'Y2m']
iSWAP_CX_seq2 = ['I', 'I', 'CX', 'Y2p', 'CX', 'I', 'I']

iSWAP_CNOT_seq1 = ['X2m', 'I', 'X2m', 'I', 'X2p']
iSWAP_CNOT_seq2 = ['I', 'CNOT', 'Y2p', 'CNOT', 'I']
#iSWAP_CX_seq1 = ['I', 'Z2m']
#iSWAP_CX_seq2 = ['CX', 'I']
iSWAP_CX_mat = evaluate_sequence(iSWAP_CX_seq1, iSWAP_CX_seq2, 'CX')*1j
iSWAP_CNOT_mat = evaluate_sequence(iSWAP_CNOT_seq1, iSWAP_CNOT_seq2, 'CNOT')

SWAP_CNOT_seq1 = ['I', 'Y2p', 'Xp', 'I', 'Y2p', 'Xp', 'I']
SWAP_CNOT_seq2 = ['CNOT', 'Y2p', 'Xp', 'CNOT', 'Y2p', 'Xp', 'CNOT']

SWAP_CX_seq1 = ['Z2p', 'I', 'X2m', 'Y2m', 'I', 'X2m', 'Y2m', 'I']
SWAP_CX_seq2 = ['I', 'CX', 'Y2p', 'Xp', 'CX', 'Y2p', 'Xp', 'CX']
SWAP_CX_mat = evaluate_sequence(SWAP_CX_seq1, SWAP_CX_seq2, 'CX')
SWAP_CNOT_mat = evaluate_sequence(SWAP_CNOT_seq1, SWAP_CNOT_seq2, 'CNOT')


seq1 = ['Xp', 'Y2p', 'I', 'I', 'I']
seq2 = ['I', 'I', 'I', 'I', 'I']
mat = evaluate_sequence(seq1, seq2, 'u')
'''

#
#seq1_to_simplify = ['Z2p', 'Y2p', 'Xp', 'Z2p']
#seq2_to_simplify = ['I', 'I', 'I', 'I']
#matrix_to_simplify = evaluate_sequence(seq1_to_simplify, seq2_to_simplify, 'CNOT')
#print('matrix to simplify', matrix_to_simplify)
#
#for i in range(24):
#    seq1_to_test = []
#    seq2_to_test = []
#    add_singleQ_clifford(i, seq1_to_test)
#    seq_len = len(seq1_to_test)
#    for j in range(seq_len):
#        seq2_to_test.append('I')
#    matrix_to_test = evaluate_sequence(seq1_to_test, seq2_to_test, 'CNOT')
#    print(i, matrix_to_simplify == matrix_to_test)
#    print(i, matrix_to_test)

#'''Test a look-up table'''
#for i in range(10):
#    print('Checking lookup table #:', i+1)
#    cliff_mat = unique_clifford_matrix_list[i]
##    print('Clifford is:', cliff_mat)
#    recovseq_1 = []
#    recovseq_2 = []
#    add_twoQ_clifford(recovery_index_list[i], recovseq_1, recovseq_2, generator = generator)
#    recov_mat = evaluate_sequence(recovseq_1, recovseq_2, generator = generator)
##    print('Recovery is:', recov_mat)
#    mat_prod = np.matmul(recov_mat, cliff_mat)
#    print('Product is:', mat_prod)