import cv2
import numpy as np

# Coordenadas de los puestos
puestos = [
    (100, 100, 167, 196), 
    (167, 100, 234, 196), 
    (234, 100, 301, 196),
    (301, 100, 368, 196), 
    (368, 100, 435, 196),
    (100, 229, 167, 325), 
    (167, 229, 234, 325), 
    (234, 229, 301, 325),
    (301, 229, 368, 325),
    (100, 325, 167, 421), 
    (167, 325, 234, 421), 
    (234, 325, 301, 421), 
    (301, 325, 368, 421),
]

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

def analisis_zona(zona):
    gris = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 100, 200)
    porcentaje_bordes = np.count_nonzero(bordes) / bordes.size
    if porcentaje_bordes < 0.05:
        return "Free", (255, 255, 255)
    else:
        color, colorrec = color_predominante(zona)
        return f"set ({color})", colorrec

def mostrar_en_vivo(url="https://10.6.169.81:8080/video"):
    video = cv2.VideoCapture(url)

    if not video.isOpened():
        print("No se pudo abrir la cámara. Se mostrará imagen blanca.")
        video = None

    while True:
        if video:
            ret, frame = video.read()
            if not ret:
                frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)
        else:
            frame = 255 * np.ones((480, 640, 3), dtype=np.uint8)

        for i, (x1, y1, x2, y2) in enumerate(puestos):
            zona = frame[y1:y2, x1:x2]
            estado, color = analisis_zona(zona)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"P{i+1}: {estado}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.imshow("Puestos de Parqueo en Vivo", frame)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if video:
        video.release()
    cv2.destroyAllWindows()

mostrar_en_vivo()
