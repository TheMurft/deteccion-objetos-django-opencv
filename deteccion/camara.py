"""Procesamiento de frames enviados por la cámara elegida en el navegador."""
import threading

import cv2
import numpy as np

from .detector import Detector, dibujar


class Camara:
    def __init__(self):
        self.detector = None
        self.lock = threading.Lock()
        self.inferencia_lock = threading.Lock()
        self.ultimas = []
        self.ultimo = None

    def procesar_frame(self, frame, conf=0.5):
        """Detecta sobre un frame del navegador y guarda el último resultado."""
        with self.inferencia_lock:
            if self.detector is None:
                self.detector = Detector()
            detecciones = self.detector.detectar(frame, conf) if self.detector.listo else []
            anotado = dibujar(frame.copy(), detecciones)
        with self.lock:
            self.ultimas, self.ultimo = detecciones, anotado
        return detecciones

    def procesar_jpeg(self, contenido, conf=0.5):
        datos = np.frombuffer(contenido, dtype=np.uint8)
        frame = cv2.imdecode(datos, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("No se pudo leer el frame enviado por el navegador.")
        return self.procesar_frame(frame, conf)

    def cerrar(self):
        with self.lock:
            self.ultimas, self.ultimo = [], None

    def instantanea(self):
        with self.lock:
            frame = None if self.ultimo is None else self.ultimo.copy()
            return frame, list(self.ultimas)


camara = Camara()
