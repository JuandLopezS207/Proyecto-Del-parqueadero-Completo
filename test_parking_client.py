import parking_client
# pip install pillow
from PIL import  Image
import io

# Intenta registrar un usuario
id=222222
password="11111"
program="Electronics Engineering"
role="professor" #debe ser en español para que funcione 
#url=" 192.168.207.57" # ip del computador
url="http://localhost:80"
print(parking_client.registerUser(url,id,password,program,role))


# Solicita un código QR al servidor (los códigos QR cambian cada fecha o cuando se reinicia el servidor)
imgBytes=parking_client.getQR(url,id,password)
# Obtiene un código QR y lo visualiza
imgBytes = parking_client.getQR(url, id, password)
image = Image.open(io.BytesIO(imgBytes))
image.show()
image.save("qr.png")
print(parking_client.sendQR(url,"qr.png"))




