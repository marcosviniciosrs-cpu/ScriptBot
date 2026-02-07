#!/usr/bin/env python3
import sys, os, subprocess, signal
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QFileSystemWatcher

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MACRO_DIR = os.path.join(BASE_DIR, "macros")
EDITOR = "xed" 

if not os.path.exists(MACRO_DIR):
    os.makedirs(MACRO_DIR)

# --- GERADORES DE ÍCONES EM MEMÓRIA ---
def get_robot_icon():
    """Desenha o robô no padrão simbólico do Cinnamon (Branco com furos)."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)

    # Cor oficial dos ícones simbólicos do Mint (Branco Gelo)
    cor_simbolica = QColor("#DEDEDE") 

    # 1. Desenha a estrutura sólida do robô
    p.setPen(Qt.NoPen)
    p.setBrush(cor_simbolica)

    # Antena
    p.drawRect(30, 8, 4, 8)      # Haste
    p.drawEllipse(28, 4, 8, 8)   # Topo

    # Orelhas
    p.drawRoundedRect(6, 26, 8, 16, 4, 4)
    p.drawRoundedRect(50, 26, 8, 16, 4, 4)

    # Cabeça
    p.drawRoundedRect(12, 16, 40, 36, 6, 6)

    # 2. O SEGREDO: Furar o desenho para os olhos e boca aparecerem como o fundo da barra
    # Usamos CompositionMode_SourceOut para "apagar" o que desenharmos agora
    p.setCompositionMode(QPainter.CompositionMode_SourceOut)
    p.setBrush(Qt.transparent) # O que for desenhado aqui vira um buraco

    # Olhos vazados
    p.drawEllipse(20, 26, 8, 8)
    p.drawEllipse(36, 26, 8, 8)

    # Boca vazada
    # Usando uma caneta grossa para "raspar" a boca no metal
    pen_vazada = QPen(Qt.transparent, 4, Qt.SolidLine, Qt.RoundCap)
    p.setPen(pen_vazada)
    p.drawLine(24, 42, 40, 42)

    p.end()
    return QIcon(pixmap)


def get_python_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setBrush(QColor("#3776AB")) 
    p.drawRoundedRect(4, 4, 16, 16, 4, 4)
    p.setBrush(QColor("#FFD43B")) 
    p.drawRoundedRect(12, 12, 16, 16, 4, 4)
    p.end()
    return QIcon(pixmap)

def get_folder_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setBrush(QColor("#EBC03F")) 
    p.drawRoundedRect(4, 8, 24, 18, 2, 2)
    p.drawRect(4, 6, 10, 5)
    p.end()
    return QIcon(pixmap)

def get_close_icon():
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#FF4B4B"), 3))
    p.drawLine(10, 10, 22, 22)
    p.drawLine(22, 10, 10, 22)
    p.end()
    return QIcon(pixmap)

class MHKManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.robo_icon = get_robot_icon()
        self.py_icon = get_python_icon()
        self.folder_icon = get_folder_icon()
        self.close_icon = get_close_icon()
        
        self.active_macros = {}
        self.tray = QSystemTrayIcon(self.robo_icon)
        self.menu = QMenu()
        
        self.watcher = QFileSystemWatcher([MACRO_DIR])
        self.watcher.directoryChanged.connect(self.rebuild_menu)
        
        self.tray.setContextMenu(self.menu)
        self.tray.setVisible(True)
        
        self.rebuild_menu()

    def add_macros_to_menu(self, menu_obj, path):
        try:
            items = sorted(os.listdir(path))
        except:
            return

        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                sub_menu = menu_obj.addMenu(self.folder_icon, item)
                self.add_macros_to_menu(sub_menu, full_path)
            elif item.endswith(".py"):
                name = item.replace(".py", "")
                act = menu_obj.addAction(self.py_icon, name)
                act.triggered.connect(lambda checked, p=full_path, n=item: self.run_macro(p, n))

    def rebuild_menu(self):
        self.menu.clear()
        self.add_macros_to_menu(self.menu, MACRO_DIR)
        self.menu.addSeparator()

        if self.active_macros:
            for filename in list(self.active_macros.keys()):
                stop_act = self.menu.addAction(self.close_icon, f"Fechar: {filename}")
                stop_act.triggered.connect(lambda checked, f=filename: self.stop_macro(f))
            self.menu.addSeparator()

        self.menu.addAction("➕ Novo Macro", self.create_macro)
        self.menu.addAction("📁 Abrir Pasta", lambda: subprocess.Popen(["xdg-open", MACRO_DIR]))
        
        self.menu.addSeparator()
        self.menu.addAction(self.close_icon, "Sair", self.quit_app)
        self.menu.adjustSize()

    def run_macro(self, full_path, filename):
        if filename in self.active_macros:
            return
        proc = subprocess.Popen([sys.executable, full_path])
        self.active_macros[filename] = proc
        self.rebuild_menu()

    def stop_macro(self, filename):
        if filename in self.active_macros:
            proc = self.active_macros[filename]
            try:
                os.kill(proc.pid, signal.SIGTERM)
            except:
                pass
            del self.active_macros[filename]
            self.rebuild_menu()

    def create_macro(self):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(None, "MHK", "Nome do Macro:")
        if ok and name:
            if not name.endswith(".py"): name += ".py"
            path = os.path.join(MACRO_DIR, name)
            if not os.path.exists(path):
                with open(path, 'w') as f: f.write("#!/usr/bin/env python3\n")
            subprocess.Popen([EDITOR, path])

    def quit_app(self):
        for name in list(self.active_macros.keys()):
            self.stop_macro(name)
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    manager = MHKManager()
    manager.run()
