""" Record reset """


import base64


rec = "999\n"
rec += "999\n"
rec += "999\n"


with open("records.db", "wb") as infile:
    data = rec.encode(encoding="utf-8")
    encoded = base64.encodebytes(data)
    infile.write(encoded)
