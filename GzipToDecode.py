import gzip
from io import BytesIO

data = b'AQUI_TU_CODIGO'
with gzip.GzipFile(fileobj=BytesIO(data)) as f:
    data_new = f.read()

print(data_new)



