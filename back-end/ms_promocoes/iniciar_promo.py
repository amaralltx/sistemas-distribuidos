import os
import subprocess
import time

def iniciar_terminais():
    diretorio_atual = os.getcwd()
    
    processos = [
        {"nome": "Consumidor C1", "arquivo": "consumidor_c1.py"},
        {"nome": "Consumidor C2", "arquivo": "consumidor_c2.py"},
        {"nome": "MS Promoções", "arquivo": "main.py"}
    ]
    
    print("Iniciando MS Promoções...")

    for processo in processos:
        print(f"Abrindo {processo['nome']}...")
        
        comando_shell = f"cd {diretorio_atual} && python3 {processo['arquivo']}"
        
        applescript = f'''
        tell application "Terminal"
            do script "{comando_shell}"
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript])
        
        time.sleep(1)

if __name__ == "__main__":
    iniciar_terminais()