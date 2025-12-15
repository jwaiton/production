from enum import Enum, auto


class processing_style(Enum):
    '''
    simple enum class to distinguish between
    processing styles. add more at your own risk!
    '''
    LDC    = "LDC"
    FOLDER = "FOLDER"
    FILE   = "FILE"
