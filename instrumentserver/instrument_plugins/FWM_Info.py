from .Qubit_Info import Qubit_Info
from .instrument import Instrument
import types

ROTATIONS = (
    'Gaussian',
    'GaussianSquare',
    'Square',
)

class FWM_Info(Qubit_Info):

    def __init__(self, name, **kwargs):
        super(FWM_Info, self).__init__(name, **kwargs)


