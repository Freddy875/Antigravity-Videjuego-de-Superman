"""
servidor_web.py — Servidor local para jugar Superman: Nivel 1 en el navegador.
Inicia un servidor HTTP local y abre automáticamente la pestaña del navegador en http://localhost:8000.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

PUERTO = 8000
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))

class ManejadorArchivos(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR_ACTUAL, **kwargs)

    def log_message(self, format, *args):
        # Silenciar logs excesivos de peticiones estáticas
        pass

def iniciar():
    os.chdir(DIR_ACTUAL)
    puerto = PUERTO
    servidor = None

    for intento in range(10):
        try:
            servidor = socketserver.TCPServer(("", puerto), ManejadorArchivos)
            break
        except OSError:
            puerto += 1

    if not servidor:
        print("No se pudo enlazar ningún puerto disponible.")
        sys.exit(1)

    url = f"http://localhost:{puerto}/index.html"
    print("=" * 60)
    print("🦸 SUPERMAN: NIVEL 1 — VERSIÓN WEB PARA NAVEGADOR")
    print("=" * 60)
    print(f"Servidor web activo en: {url}")
    print("Abriendo el juego en tu navegador web predeterminado...")
    print("Para detener el servidor, presiona Ctrl + C en esta consola.")
    print("=" * 60)

    webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor web detenido.")
        servidor.server_close()

if __name__ == "__main__":
    iniciar()
