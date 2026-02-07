import pyautogui
import time
import sys
from pynput import keyboard
import threading

# --- CONFIGURAÇÕES (Edite aqui) ---

COOR_1 = (284, 426) 
COOR_2 = (369,562)
COOR_3 = (1199, 672)

# Delay geral entre cliques (em milissegundos)
DELAY_MS = 200

# SAÍDA DE EMERGÊNCIA: Tempo máximo de execução em segundos
# (Exemplo: 300 para 5 minutos, ou 60 para 1 minuto)
TEMPO_LIMITE_SEGUNDOS = 300 

# ---------------------------------

delay_segundos = DELAY_MS / 1000
executando = True
inicio_script = time.time() # Registra o momento exato do início

def monitorar_cancelamento():
    global executando
    def ao_pressionar(key):
        if key == keyboard.Key.f9:
            print("\n[!] Interrupção manual (F9) detectada! Encerrando...")
            global executando
            executando = False
            return False 

    with keyboard.Listener(on_press=ao_pressionar) as listener:
        listener.join()

def verificar_timeout():
    """Verifica se o tempo limite de segurança foi atingido."""
    global executando
    tempo_passado = time.time() - inicio_script
    if tempo_passado >= TEMPO_LIMITE_SEGUNDOS:
        print(f"\n[!!!] SAÍDA DE EMERGÊNCIA: Limite de {TEMPO_LIMITE_SEGUNDOS}s atingido.")
        executando = False
        return True
    return False

def executar_passos():
    global executando
    
    passos = [COOR_1, COOR_2, COOR_3]
    
    for i, coor in enumerate(passos, 1):
        # Verifica o tempo e o F9 antes de cada clique
        if not executando or verificar_timeout(): return
        
        print(f"Passo {i}: Movendo para {coor} e clicando...")
        pyautogui.moveTo(coor[0], coor[1])
        pyautogui.click()
        time.sleep(delay_segundos)

    # Finaliza com ESC
    if not executando or verificar_timeout(): return
    print("Apertando ESC...")
    pyautogui.press('esc')
    time.sleep(delay_segundos)

if __name__ == "__main__":
    thread_cancelar = threading.Thread(target=monitorar_cancelamento, daemon=True)
    thread_cancelar.start()

    print("=== MACRO INICIADO ===")
    print(f"Tempo limite de segurança: {TEMPO_LIMITE_SEGUNDOS} segundos.")
    print("Pressione F9 para PARAR o script manualmente.")
    print("Iniciando em 3 segundos...")
    time.sleep(3)
    
    # Reinicia o contador após o delay inicial de 3s para ser mais preciso
    inicio_script = time.time() 
    
    while executando:
        if verificar_timeout():
            break
        executar_passos()
        if executando:
            print(f"Ciclo completo. Tempo decorrido: {int(time.time() - inicio_script)}s")
    
    print("---")
    print("Script finalizado/encerrado.")
