"""Detección de objetos con OpenCV (cv2.dnn) usando un modelo YOLO en formato ONNX."""
import cv2
import numpy as np
from django.conf import settings
TAM = 640

# Nombre de la clase en el modelo (minúsculas) -> etiqueta que ve el usuario
ALIAS = {
    "fall-detected": "Caída detectada",
    "gloves": "Guantes",
    "goggles": "Gafas de seguridad",
    "hardhat": "Casco",
    "mask": "Mascarilla",
    "no-gloves": "Sin guantes",
    "no-goggles": "Sin gafas",
    "no-hardhat": "Sin casco",
    "no-mask": "Sin mascarilla",
    "no-safety vest": "Sin chaleco",
    "no_harness": "Sin arnés",
    "person": "Persona",
    "safety vest": "Chaleco de seguridad",
}

COLORES = {
    "Caída detectada": (0, 0, 255),
    "Guantes": (80, 200, 60),
    "Gafas de seguridad": (220, 140, 40),
    "Casco": (220, 140, 40),
    "Mascarilla": (80, 200, 60),
    "Sin guantes": (0, 0, 255),
    "Sin gafas": (0, 0, 255),
    "Sin casco": (0, 0, 255),
    "Sin mascarilla": (0, 0, 255),
    "Sin chaleco": (0, 0, 255),
    "Sin arnés": (0, 0, 255),
    "Persona": (255, 255, 255),
    "Chaleco de seguridad": (80, 200, 60),
}


class Detector:
    def __init__(self):
        self.net, self.clases = None, []
        if settings.MODELO_ONNX.exists() and settings.MODELO_CLASES.exists():
            ruta_modelo = settings.MODELO_ONNX.resolve()
            self.net = cv2.dnn.readNetFromONNX(str(ruta_modelo))
            with open(settings.MODELO_CLASES, encoding="utf-8") as f:
                self.clases = [l.strip().lower() for l in f if l.strip()]

    @property
    def listo(self):
        return self.net is not None

    def detectar(self, frame, conf_min=0.5, nms=0.45):
        """Devuelve una lista de (etiqueta, confianza, (x, y, w, h))."""
        if not self.listo:
            return []
        alto, ancho = frame.shape[:2]
        # YOLO se entrenó con letterbox: conserva la proporción de la imagen
        # y completa el espacio restante con gris, en vez de deformar el frame.
        escala = min(TAM / ancho, TAM / alto)
        nuevo_ancho = int(round(ancho * escala))
        nuevo_alto = int(round(alto * escala))
        reducido = cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)
        pad_x = (TAM - nuevo_ancho) // 2
        pad_y = (TAM - nuevo_alto) // 2
        entrada = np.full((TAM, TAM, 3), 114, dtype=np.uint8)
        entrada[pad_y:pad_y + nuevo_alto, pad_x:pad_x + nuevo_ancho] = reducido
        blob = cv2.dnn.blobFromImage(entrada, 1 / 255.0, (TAM, TAM), swapRB=True, crop=False)
        self.net.setInput(blob)
        salida = np.asarray(self.net.forward())
        if salida.ndim == 3:
            salida = salida[0]
        if salida.ndim != 2:
            raise ValueError(f"Salida ONNX inesperada: forma {salida.shape}.")

        dimensiones_clase = len(self.clases) + 4
        if salida.shape[0] == dimensiones_clase:
            salida = salida.T
        elif salida.shape[1] != dimensiones_clase:
            raise ValueError(
                f"El ONNX produce {salida.shape}, pero clases.txt contiene "
                f"{len(self.clases)} clases (se esperaban {dimensiones_clase} valores por predicción). "
                "Verifica que clases.txt corresponda exactamente al modelo y esté en el orden de entrenamiento."
            )

        por_clase = {}
        for prediccion in salida:
            puntajes = prediccion[4:dimensiones_clase]
            id_clase = int(np.argmax(puntajes))
            confianza = float(puntajes[id_clase])
            if confianza < conf_min or id_clase >= len(self.clases):
                continue
            etiqueta = ALIAS.get(self.clases[id_clase])
            if etiqueta is None:
                continue

            cx, cy, ancho_caja, alto_caja = map(float, prediccion[:4])
            x1 = int(round((cx - ancho_caja / 2 - pad_x) / escala))
            y1 = int(round((cy - alto_caja / 2 - pad_y) / escala))
            x2 = int(round((cx + ancho_caja / 2 - pad_x) / escala))
            y2 = int(round((cy + alto_caja / 2 - pad_y) / escala))
            x1, x2 = np.clip([x1, x2], 0, ancho)
            y1, y2 = np.clip([y1, y2], 0, alto)
            caja_ancho, caja_alto = int(x2 - x1), int(y2 - y1)
            if caja_ancho <= 0 or caja_alto <= 0:
                continue
            por_clase.setdefault(id_clase, []).append(
                ([int(x1), int(y1), caja_ancho, caja_alto], confianza, etiqueta)
            )

        # NMS independiente por clase para que objetos PPE no eliminen la caja Persona.
        resultado = []
        for candidatos in por_clase.values():
            cajas = [candidato[0] for candidato in candidatos]
            confianzas = [candidato[1] for candidato in candidatos]
            indices = cv2.dnn.NMSBoxes(cajas, confianzas, conf_min, nms)
            if len(indices) == 0:
                continue
            for indice in np.asarray(indices).reshape(-1):
                caja, confianza, etiqueta = candidatos[int(indice)]
                resultado.append((etiqueta, confianza, tuple(caja)))
        return resultado


def dibujar(frame, detecciones):
    """Dibuja recuadros y etiquetas sobre el fotograma."""
    for etiqueta, conf, (x, y, w, h) in detecciones:
        color = COLORES.get(etiqueta, (255, 255, 255))
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        texto = f"{etiqueta} {conf:.2f}"
        cv2.putText(frame, texto, (x, max(y - 8, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame
