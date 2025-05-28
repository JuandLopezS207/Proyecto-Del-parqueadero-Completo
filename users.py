from pyzbar.pyzbar import decode
from PIL import Image
from json import dumps, loads
from hashlib import sha256
from Crypto.Cipher import AES
import base64
import pyqrcode
from os import urandom
import io
from datetime import datetime
import cv2
import numpy as np

# Se lee el archivo de usuarios, si no existe se crea uno nuevo
usersFileName = "users.txt"
try:
    archivo = open(usersFileName, "x")
    archivo.close()
except FileExistsError:
    pass

# Verifica el color predominante de la zona
def color_predominante(region):
    promedio_b = np.mean(region[:, :, 0])
    promedio_g = np.mean(region[:, :, 1])
    promedio_r = np.mean(region[:, :, 2])
    
    if promedio_b > promedio_g and promedio_b > promedio_r:
        return "B", (255, 0, 0)
    elif promedio_g > promedio_b and promedio_g > promedio_r:
        return "G", (0, 255, 0)
    elif promedio_r > promedio_b and promedio_r > promedio_g:
        return "R", (0, 0, 255)
    else:
        return "Indefinido", (255, 255, 255)

# Determina si la zona está libre u ocupada
def analisis_zona(zona):
    gris = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 100, 200)
    porcentaje_bordes = np.count_nonzero(bordes) / bordes.size
    
    if porcentaje_bordes < 0.05:
        return "Free", (255, 255, 255)
    else:
        color, colorrec = color_predominante(zona)
        return f"set ({color})", colorrec

# Definición de los puestos en términos de píxeles (x1,y1,x2,y2)
puestos = [
    (100, 100, 167, 196), (167, 100, 234, 196), (234, 100, 301, 196),
    (301, 100, 368, 196), (368, 100, 435, 196), (100, 229, 167, 325),
    (167, 229, 234, 325), (234, 229, 301, 325), (301, 229, 368, 325),
    (100, 325, 167, 421), (167, 325, 234, 421), (234, 325, 301, 421),
    (301, 325, 368, 421),
]

date = None
key = None

def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
    return (ciphertext, aesCipher.nonce, authTag)

def decrypt_AES_GCM(encryptedMsg, secretKey):
    (ciphertext, nonce, authTag) = encryptedMsg
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

def generateQR(id, program, role, buffer):
    global key, date
    data = {'id': id, 'program': program, 'role': role}
    datas = dumps(data).encode("utf-8")

    if key is None or date != datetime.today().strftime('%Y-%m-%d'):
        key = urandom(32)
        date = datetime.today().strftime('%Y-%m-%d')

    encrypted = list(encrypt_AES_GCM(datas, key))
    qr_text = dumps({
        'qr_text0': base64.b64encode(encrypted[0]).decode('ascii'),
        'qr_text1': base64.b64encode(encrypted[1]).decode('ascii'),
        'qr_text2': base64.b64encode(encrypted[2]).decode('ascii')
    })

    qrcode = pyqrcode.create(qr_text)
    qrcode.png(buffer, scale=8)
    buffer.seek(0)
    return buffer

# Registra un nuevo usuario en el sistema
def registerUser(id, password, program, role):
    with open(usersFileName, "r") as archivo:
        users = archivo.readlines()

    for user in users:
        partes = user.strip().split(',')
        if len(partes) == 0:
            continue
        if partes[0] == str(id):
            return "User already registered"

    with open(usersFileName, "a") as archivo:
        archivo.write(f"{id},{password},{program},{role}\n")
    
    return "User succesfully registered"

# Genera un código QR para el usuario
def getQR(id, password):
    with open(usersFileName, "r") as archivo:
        users = archivo.readlines()

    buffer = io.BytesIO()
    for user in users:
        partes = user.strip().split(',')
        if partes[0] == str(id) and partes[1] == password:
            return generateQR(id, partes[2], partes[3], buffer)

    return "Usuario no registrado"

# Procesa el QR y asigna un puesto de estacionamiento
def sendQR(qr_text_data):
    global key

    roles_puestos = {
        "professor": range(0, 3),
        "student": range(3, 8),
        "otros": range(8, 14)
    }

    try:
        data = loads(qr_text_data)
        decrypted = loads(decrypt_AES_GCM((
            base64.b64decode(data["qr_text0"]),
            base64.b64decode(data["qr_text1"]),
            base64.b64decode(data["qr_text2"])
        ), key))

        usuariorol = decrypted["role"].lower()
        usuarioid = int(decrypted["id"])

        with open(usersFileName, "r") as archivo:
            users = archivo.readlines()

        encontrado = False
        for user in users:
            partes = user.strip().split(',')
            if int(partes[0]) == usuarioid:
                encontrado = True
                break

        if not encontrado:
            return "Error, el usuario no está registrado"

        video = cv2.VideoCapture("https://10.6.169.81:8080/video")
        ret, frame = video.read()
        video.release()

        if not ret:
            return "Error, no se pudo capturar la imagen de la cámara del parqueadero"

        puestos_libres = []
        for i, (px1, py1, px2, py2) in enumerate(puestos):
            zona = frame[py1:py2, px1:px2]
            texto, _ = analisis_zona(zona)
            if texto == "Free":
                puestos_libres.append(i)

        rol = usuariorol if usuariorol in roles_puestos else "otros"

        for i in roles_puestos[rol]:
            if i in puestos_libres:
                return f"Puesto asignado: {i + 1}"

        return "No hay puestos disponibles para su rol"

    except Exception as e:
        return "Error, la clave ha expirado o el QR no es válido, o un error inesperado."
