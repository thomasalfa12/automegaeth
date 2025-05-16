from web3 import Web3

TOKEN_OUTS = [
    "0xe9b6e75c243b6100ffcb1c66e8f78f96feea727f",  # CUSD
    "0xfaf334e157175ff676911adcf0964d7f54f2c424",  # tkUSDC
    "0x9629684df53db9e4484697d0a50c442b2bfa80a8",  # GTE
    "0x7f11aa697e05b75600354ac9acf8bb209225e932",  # Bitcoin
    "0x10a6be7d23989d00d528e68cf8051d095f741145",  # Mega
    "0x176735870dc6c22b4ebfbf519de2ce758de78d94",
    "0x1d2e159712c1a109fa869cc9fef0e3e60abd542b",
    "0xf82ff0799448630eb56ce747db840a2e02cde4d8",
    "0x1aa388c43474979c598d1a37309d2f6422a38dfc",
    "0xa626f15d10f2b30af1fb0d017f20a579500b5029",
    "0xbba08cf5ece0cc21e1deb5168746c001b123a756",
    "0x8d635c4702ba38b1f1735e8e784c7265dcc0b623"
]

TOKEN_OUTS = [Web3.to_checksum_address(addr) for addr in TOKEN_OUTS]
