import ctypes
import base64
import os
from platform import system


# MASK // The default mask if not passed is: ???/????
# 'A'  // Non digit
# '9'  // Digit
# '_'  // Digit or non digit
# '*'  // Optional Non Digit
# '0'  // Optional Digit
# '?'  // Optional Digit or Non Digit
# '/'  // Motorcycle row split ( If not set, the default is after the third character)


"""
 ANPR_LOAD_OK                    (1)
 ANPR_TOKEN_NOT_FOUND            (0xFFFF0001)
 ANPR_TOKEN_VALIDATION_EXPIRED   (0xFFFF0002)
 ANPR_TOKEN_KEY_ERROR            (0xFFFF0003)
 ANPR_FILES_NOT_FOUND            (0xFFFF0004)
 ANPR_GENERAL_EXCEPTION          (0xFFFF0005)
"""


class DataTrafficOCR:
    """
    This class will be used to contain the entire OCR process
    """

    DEFAULT_MASK = '???/????';
    BRAZIL_MASK_OLD_ONLY = 'AAA/9999';
    BRAZIL_MASK_NEW_ONLY = 'AAA/9A99';
    BRAZIL_MASK = 'AAA/9_99';

    # flags
    ANPR_DEFAULT =                (0)
    ANPR_NO_CHARS_JSON =          (1 << 0)
    ANPR_NO_MOTORCYCLE_JSON =     (1 << 1)
    ANPR_NO_TEXT_COLOR_JSON =     (1 << 2)

    # code error
    CODES = {
        '0': 'ANPR_STATUS_LOAD_OK',
        '1': 'ANPR_STATUS_TOKEN_NOT_FOUND',
        '2': 'ANPR_STATUS_TOKEN_VALIDATION_EXPIRED',
        '3': 'ANPR_STATUS_TOKEN_KEY_ERROR',
        '4': 'ANPR_STATUS_FILES_NOT_FOUND',
        '5': 'ANPR_STATUS_CALL_NOT_SUPPORTED',
        '6': 'ANPR_STATUS_GENERAL_EXCEPTION'
    }

    def __init__(self, respath, library_path, **kwargs):
        self.__respath = respath
        self.__library_path = library_path
        self.__mask = kwargs.get('mask') if kwargs.get('mask') else None
        self.__flags = kwargs.get('flags') if kwargs.get('flags') else DataTrafficOCR.ANPR_NO_CHARS_JSON
        self.__onWeights = kwargs.get('on_weights') if kwargs.get('on_weights') else False
        
        if 'Linux' in system():
            dll_name = "libanpr.so"
        else: # Windows
            dll_name = "anpr.dll"

        # Check that dll exisits
        abs_base_path = os.path.abspath(self.__library_path)
        lib_path = abs_base_path+ os.sep + dll_name

        # Error code
        self.exit_code = ctypes.c_uint64()

        # Create cdll obj
        self.ocr_dll = ctypes.CDLL(lib_path)

        self.ocr_dll.C_ReadBase64JPG.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.ocr_dll.C_ReadBase64JPG.restype = ctypes.c_void_p

        self.ocr_dll.C_ReadBytes.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        self.ocr_dll.C_ReadBytes.restype = ctypes.c_void_p

        self.ocr_dll.C_FreeResult.argtypes = [ctypes.c_void_p]
        self.ocr_dll.C_FreeResult.restype = None

        self.ocr_dll.ANPR_CreateDefaultFromFile.argtypes = [ctypes.c_char_p]
        self.ocr_dll.ANPR_CreateDefaultFromFile.restype = ctypes.c_void_p

        self.ocr_dll.ANPR_CreateFromFile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32]
        self.ocr_dll.ANPR_CreateFromFile.restype = ctypes.c_void_p

        self.ocr_dll.ANPR_CreateDefault.argtypes = None
        self.ocr_dll.ANPR_Create.restype = ctypes.c_void_p

        self.ocr_dll.ANPR_Create.argtypes = [ctypes.c_char_p, ctypes.c_int32]
        self.ocr_dll.ANPR_Create.restype = ctypes.c_void_p

        self.ocr_dll.C_GetVersion.argtypes = None
        self.ocr_dll.C_GetVersion.restype = ctypes.c_char_p

        self.ocr_dll.C_GetWVersion.argtypes = None
        self.ocr_dll.C_GetWVersion.restype = ctypes.c_char_p

        # Instance anpr        
        if not self.__mask and not self.__onWeights:
            self.anpr_point = self.ocr_dll.ANPR_CreateDefault()

        elif not self.__mask and self.__onWeights:
            self.anpr_point = self.ocr_dll.ANPR_CreateDefaultFromFile(self.__respath.encode())
        
        elif self.__mask and not self.__onWeights:
            self.anpr_point = self.ocr_dll.ANPR_Create(self.__mask.encode(), self.__flags)
        
        else:
            self.anpr_point = self.ocr_dll.ANPR_CreateFromFile(self.__respath.encode(), self.__mask.encode(), self.__flags)
            
        if not self.anpr_point:
            raise RuntimeError("ANPR Could not be initialized. Check if respath points to the right directory")


    def ocr(self, img_path, debug=False):
        with open(img_path, "rb") as img_file:
            data = img_file.read()
            result_pointer = self.ocr_dll.C_ReadBytes(self.anpr_point, data, len(data))
            if debug:
                result_pointer = self.ocr_dll.C_ReadBytesDebug(self.anpr_point, data, len(data))
            else:
                result_pointer = self.ocr_dll.C_ReadBytes(self.anpr_point, data, len(data))
            result = ctypes.cast(result_pointer, ctypes.c_char_p).value
            self.ocr_dll.C_FreeResult(result_pointer)
            return result

    def ocr_image_encoded(self, image_encoded):
        base64_encoded = base64.b64encode(image_encoded)
        result_pointer = self.ocr_dll.C_ReadBase64JPG(self.anpr_point, base64_encoded)
        result = ctypes.cast(result_pointer, ctypes.c_char_p).value
        self.ocr_dll.C_FreeResult(result_pointer)
        return result

    def get_error_code(self):
        #strHex = "0x%0.2X" % self.exit_code.value
        return DataTrafficOCR.CODES[str(self.exit_code.value)]

    def getVersion(self):
        return self.ocr_dll.C_GetVersion().decode()

    def getWVersion(self):
        return self.ocr_dll.C_GetWVersion().decode()