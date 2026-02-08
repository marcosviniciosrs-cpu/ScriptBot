#!/usr/bin/env python3
import sys, os, subprocess, signal
from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QInputDialog)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QFileSystemWatcher

# --- CONFIGURAÇÕES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MACRO_DIR = os.path.join(BASE_DIR, "macros")
EDITOR = "xed" 

if not os.path.exists(MACRO_DIR):
    os.makedirs(MACRO_DIR)

# --- GERADORES DE ÍCONES (Mantidos conforme seu original) ---
def get_robot_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    cor_simbolica = QColor("#DEDEDE") 
    p.setPen(Qt.NoPen)
    p.setBrush(cor_simbolica)
    p.drawRect(30, 8, 4, 8); p.drawEllipse(28, 4, 8, 8) # Antena
    p.drawRoundedRect(6, 26, 8, 16, 4, 4); p.drawRoundedRect(50, 26, 8, 16, 4, 4) # Orelhas
    p.drawRoundedRect(12, 16, 40, 36, 6, 6) # Cabeça
    p.setCompositionMode(QPainter.CompositionMode_SourceOut)
    p.setBrush(Qt.transparent)
    p.drawEllipse(20, 26, 8, 8); p.drawEllipse(36, 26, 8, 8) # Olhos
    p.setPen(QPen(Qt.transparent, 4, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(24, 42, 40, 42) # Boca
    p.end()
    return QIcon(pixmap)

def get_python_icon():
    pixmap = QPixmap(32, 32); pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setBrush(QColor("#3776AB")); p.drawRoundedRect(4, 4, 16, 16, 4, 4)
    p.setBrush(QColor("#FFD43B")); p.drawRoundedRect(12, 12, 16, 16, 4, 4)
    p.end()
    return QIcon(pixmap)

def get_close_icon():
    pixmap = QPixmap(32, 32); pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#FF4B4B"), 3))
    p.drawLine(10, 10, 22, 22); p.drawLine(22, 10, 10, 22)
    p.end()
    return QIcon(pixmap)

class MHKManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.robo_icon = get_robot_icon()
        self.py_icon = get_python_icon()
        self.close_icon = get_close_icon()
        
        self.active_macros = {}
        self.tray = QSystemTrayIcon(self.robo_icon)
        self.menu = QMenu()
        
        self.watcher = QFileSystemWatcher([MACRO_DIR])
        self.watcher.directoryChanged.connect(self.rebuild_menu)
        
        self.tray.setContextMenu(self.menu)
        self.tray.setVisible(True)
        
        self.rebuild_menu()

    def add_macros_to_menu(self):
        """Varre a pasta macros procurando por subpastas com main.py"""
        try:
            items = sorted(os.listdir(MACRO_DIR))
        except:
            return

        for item in items:
            folder_path = os.path.join(MACRO_DIR, item)
            
            # Só nos interessam DIRETÓRIOS (Pastas)
            if os.path.isdir(folder_path):
                # Ignora a própria venv do ScriptBot ou pastas ocultas
                if item == "venv" or item.startswith("."):
                    continue
                
                main_file = os.path.join(folder_path, "main.py")
                
                # Só adiciona ao menu se existir um 'main.py' dentro da pasta
                if os.path.exists(main_file):
                    act = self.menu.addAction(self.py_icon, item) # O nome no menu é o nome da pasta
                    act.triggered.connect(lambda checked, p=main_file, n=item: self.run_macro(p, n))

    def rebuild_menu(self):
        self.menu.clear()
        
        # 1. Lista os Macros Padronizados
        self.add_macros_to_menu()
        
        self.menu.addSeparator()

        # 2. Macros Ativos (Para fechar)
        if self.active_macros:
            for name in list(self.active_macros.keys()):
                stop_act = self.menu.addAction(self.close_icon, f"Parar: {name}")
                stop_act.triggered.connect(lambda checked, n=name: self.stop_macro(n))
            self.menu.addSeparator()

        # 3. Opções de Gerenciamento
        self.menu.addAction("➕ Novo Macro (Pasta)", self.create_macro)
        self.menu.addAction("📁 Abrir Pasta Macros", lambda: subprocess.Popen(["xdg-open", MACRO_DIR]))
        
        self.menu.addSeparator()
        self.menu.addAction(self.close_icon, "Sair", self.quit_app)
        self.menu.adjustSize()

    def run_macro(self, main_path, macro_name):
        if macro_name in self.active_macros:
            return

        # Caminho da venv específica deste macro
        macro_dir = os.path.dirname(main_path)
        venv_python = os.path.join(macro_dir, "venv", "bin", "python3")

        # Se existir uma venv na pasta do macro, usa ela. Senão, usa o Python do ScriptBot.
        executable = venv_python if os.path.exists(venv_python) else sys.executable

        proc = subprocess.Popen([executable, main_path], cwd=macro_dir)
        self.active_macros[macro_name] = proc
        self.rebuild_menu()

    def stop_macro(self, name):
        if name in self.active_macros:
            proc = self.active_macros[name]
            try:
                os.kill(proc.pid, signal.SIGTERM)
            except:
                pass
            del self.active_macros[name]
            self.rebuild_menu()

    def create_macro(self):
        """Cria uma pasta, um main.py e abre o editor."""
        name, ok = QInputDialog.getText(None, "ScriptBot", "Nome da nova pasta do Macro:")
        if ok and name:
            new_macro_dir = os.path.join(MACRO_DIR, name)
            main_file = os.path.join(new_macro_dir, "main.py")
            
            if not os.path.exists(new_macro_dir):
                os.makedirs(new_macro_dir)
            
            if not os.path.exists(main_file):
                with open(main_file, 'w') as f:
                    f.write("#!/usr/bin/env python3\nimport os\nprint('Macro Iniciado!')\n")
            
            subprocess.Popen([EDITOR, main_file])
            self.rebuild_menu()

    def quit_app(self):
        for name in list(self.active_macros.keys()):
            self.stop_macro(name)
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    manager = MHKManager()
    manager.run()