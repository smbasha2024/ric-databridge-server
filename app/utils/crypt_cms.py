from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
import binascii

#TripleDESCryptoServiceProvider
#Mode = CBC
#Key = HexToBytes(actionKey)
#IV  = HexToBytes(actionIv)
#Input Encoding = ASCII
#Output = HEX STRING

class CryptoCMS:

    # MUST be same values from .NET
    actionKey = "EA81AA1D5FC1EC53E84F30AA746139EEBAFF8A9B76638895"      # <-- your real hex key
    actionIv = "87AF7EA221F3FFF5"      # <-- your real hex IV

    actionKeymobile = "A4B7F0E9C2D185637A9F4E2B5C8D0A1E3F2B4C5D6E7F8A9B"
    actionIvmobile = "054DE56C075E1390"

    dtbrdg_actionKey = "167DE95489F2CC86AEAAC719A36712AC4EA4DF7C88B5BDEA"
    dtbrdg_actionIv = "E3541F80197CE54B"

    # -----------------------------------------
    # Helpers (Exact .NET Equivalent)
    # -----------------------------------------
    @staticmethod
    def hex_to_bytes(hex_string: str) -> bytes:
        return bytes.fromhex(hex_string)

    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        return binascii.hexlify(data).decode("ascii").upper()

    # -----------------------------------------
    # CORE ENCRYPT
    # -----------------------------------------
    @staticmethod
    def encrypt(data: str, key_hex: str, iv_hex: str) -> str:

        key = CryptoCMS.hex_to_bytes(key_hex)
        iv = CryptoCMS.hex_to_bytes(iv_hex)

        cipher = DES3.new(key, DES3.MODE_CBC, iv)

        encrypted = cipher.encrypt(
            pad(data.encode("ascii"), DES3.block_size)
        )

        return CryptoCMS.bytes_to_hex(encrypted)

    # -----------------------------------------
    # CORE DECRYPT
    # -----------------------------------------
    @staticmethod
    def decrypt(data: str, key_hex: str, iv_hex: str) -> str:

        key = CryptoCMS.hex_to_bytes(key_hex)
        iv = CryptoCMS.hex_to_bytes(iv_hex)

        cipher = DES3.new(key, DES3.MODE_CBC, iv)

        decrypted = cipher.decrypt(
            CryptoCMS.hex_to_bytes(data)
        )

        return unpad(decrypted, DES3.block_size).decode("ascii")

    # -----------------------------------------
    # Action Methods (Match .NET)
    # -----------------------------------------
    @staticmethod
    def action_encrypt(data: str) -> str:
        return CryptoCMS.encrypt(data, CryptoCMS.actionKey, CryptoCMS.actionIv)

    @staticmethod
    def action_decrypt(data: str) -> str:
        return CryptoCMS.decrypt(data, CryptoCMS.actionKey, CryptoCMS.actionIv)

    @staticmethod
    def action_mobile_encrypt(data: str) -> str:
        return CryptoCMS.encrypt(data,
                              CryptoCMS.actionKeymobile,
                              CryptoCMS.actionIvmobile)

    @staticmethod
    def action_mobile_decrypt(data: str) -> str:
        return CryptoCMS.decrypt(data,
                              CryptoCMS.actionKeymobile,
                              CryptoCMS.actionIvmobile)
    
    @staticmethod
    def action_dtbrdg_encrypt(data: str) -> str:
        return CryptoCMS.encrypt(data,
                              CryptoCMS.dtbrdg_actionKey,
                              CryptoCMS.dtbrdg_actionIv)

    @staticmethod
    def action_dtbrdg_decrypt(data: str) -> str:
        return CryptoCMS.decrypt(data,
                              CryptoCMS.dtbrdg_actionKey,
                              CryptoCMS.dtbrdg_actionIv)