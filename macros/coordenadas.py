import tkinter as tk
import pyautogui
import pyperclip
from pynput import mouse, keyboard

# Variável para rastrear o estado da tecla CTRL
ctrl_pressionado = False

def mostrar_aviso_copiado(x, y, texto):
    aviso = tk.Toplevel(root)
    aviso.overrideredirect(True)
    aviso.attributes('-topmost', True)
    aviso.geometry(f"+{x+20}+{y-20}")
    
    label_aviso = tk.Label(aviso, text=f"Copiado: {texto}", 
                           font=('Consolas', 10, 'bold'),
                           bg='#00ff00', fg='#000000', 
                           padx=5, pady=2, borderwidth=1, relief="solid")
    label_aviso.pack()
    aviso.after(3000, aviso.destroy)

def ao_clicar(x, y, button, pressed):
    # Só copia se o botão esquerdo for clicado ENQUANTO o CTRL estiver segurado
    if button == mouse.Button.left and pressed and ctrl_pressionado:
        texto = f"{int(x)},{int(y)}"
        pyperclip.copy(texto)
        root.after(0, lambda: mostrar_aviso_copiado(int(x), int(y), texto))

# Funções para monitorar o teclado (CTRL)
def ao_pressionar_tecla(key):
    global ctrl_pressionado
    if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressionado = True

def ao_soltar_tecla(key):
    global ctrl_pressionado
    if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        ctrl_pressionado = False

def atualizar_coordenadas():
    x, y = pyautogui.position()
    label.config(text=f"X: {x} | Y: {y}")
    toolbox.geometry(f"+{x+20}+{y+20}")
    root.after(10, atualizar_coordenadas)

# --- Listeners ---
# Monitora o Mouse
mouse_listener = mouse.Listener(on_click=ao_clicar)
mouse_listener.start()

# Monitora o Teclado (para o CTRL)
keyboard_listener = keyboard.Listener(on_press=ao_pressionar_tecla, on_release=ao_soltar_tecla)
keyboard_listener.start()

# --- Interface Gráfica ---
root = tk.Tk()
root.withdraw()

toolbox = tk.Toplevel(root)
toolbox.overrideredirect(True)
toolbox.attributes('-topmost', True)

label = tk.Label(toolbox, font=('Consolas', 11, 'bold'), 
                 bg='#2e2e2e', fg='#00ff00', 
                 padx=10, pady=5, 
                 borderwidth=2, relief="solid")
label.pack()

atualizar_coordenadas()
root.mainloop()
