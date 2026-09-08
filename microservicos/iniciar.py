import subprocess
import sys
import time
import os

pastas_ms = [
    "ms_estoque",
    "ms_pagamento",
    "ms_entrega",
    # "ms_promocoes", 
    "ms_principal"
]

print("Iniciando o ecossistema de microsserviços em janelas separadas...\n")

base_dir = os.path.abspath(os.getcwd())

for pasta in pastas_ms:
    caminho_absoluto = os.path.join(base_dir, pasta)
    
    comando_applescript = f'''
    tell application "Terminal"
        activate
        do script "cd '{caminho_absoluto}' && '{sys.executable}' main.py"
    end tell
    '''
    
    # Mudamos para subprocess.run para capturar melhor a execução
    subprocess.run(['osascript', '-e', comando_applescript])
    time.sleep(1.5)

print("\nTodos os serviços foram lançados!")