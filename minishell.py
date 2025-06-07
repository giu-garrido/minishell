import os
import sys
import subprocess
import shlex
import threading
from pathlib import Path

# Variável global para controlar o loop do shell
running = True

def parse_command(cmd_str):
    """Parse um comando individual, detectando redirecionamento"""
    cmd_str = cmd_str.strip()
    if not cmd_str:
        return None, None
    
    # Verificar redirecionamento de saída
    output_file = None
    if '>' in cmd_str:
        parts = cmd_str.split('>', 1)
        cmd_str = parts[0].strip()
        output_file = parts[1].strip()
    
    # Dividir em argumentos usando shlex para tratar aspas
    try:
        args = shlex.split(cmd_str)
    except ValueError:
        # Tentar divisão simples se houver erro no parsing
        args = cmd_str.split()
    
    return args, output_file

def cmd_pwd():
    """Comando interno: pwd"""
    print(os.getcwd())

def cmd_cd(args):
    """Comando interno: cd"""
    if len(args) != 2:
        # Sem argumentos ou mais de um argumento - não faz nada
        return
    
    try:
        os.chdir(args[1])
    except (FileNotFoundError, NotADirectoryError):
        print("no such file or directory")
    except PermissionError:
        print("permission denied")

def cmd_cat(args):
    """Comando interno: cat"""
    if len(args) < 2:
        print("cat: missing file argument")
        return
    
    for filename in args[1:]:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                print(file.read(), end='')
        except FileNotFoundError:
            print(f"cat: {filename}: no such file or directory")
        except PermissionError:
            print(f"cat: {filename}: permission denied")
        except UnicodeDecodeError:
            try:
                # Tentar com codificação latin-1 se UTF-8 falhar
                with open(filename, 'r', encoding='latin-1') as file:
                    print(file.read(), end='')
            except Exception:
                print(f"cat: {filename}: cannot read file")

def cmd_ls():
    """Comando interno: ls"""
    try:
        entries = []
        for item in os.listdir('.'):
            if not item.startswith('.'):  # Não mostrar arquivos ocultos
                entries.append(item)
        
        entries.sort()
        for entry in entries:
            print(entry, end='  ')
        if entries:
            print()  # Nova linha no final
    except PermissionError:
        print("ls: permission denied")

def cmd_echo(args):
    """Comando interno: echo"""
    if len(args) > 1:
        print(' '.join(args[1:]))
    else:
        print()

def is_builtin(command):
    """Verifica se é um comando interno"""
    builtins = ['exit', 'pwd', 'cd', 'cat', 'ls', 'echo']
    return command in builtins

def execute_builtin(args):
    """Executa comandos internos"""
    global running
    
    if not args:
        return False
    
    command = args[0]
    
    if command == 'exit':
        running = False
        return True
    elif command == 'pwd':
        cmd_pwd()
        return True
    elif command == 'cd':
        cmd_cd(args)
        return True
    elif command == 'cat':
        cmd_cat(args)
        return True
    elif command == 'ls':
        cmd_ls()
        return True
    elif command == 'echo':
        cmd_echo(args)
        return True
    
    return False

def execute_external(args, output_file=None, background=False):
    """Executa comandos externos"""
    if not args:
        return
    
    try:
        # Preparar redirecionamento
        stdout = None
        if output_file:
            stdout = open(output_file, 'w', encoding='utf-8')
        
        # Executar comando
        if background:
            # Comando em background
            subprocess.Popen(args, stdout=stdout, stderr=subprocess.PIPE)
        else:
            # Comando em foreground
            result = subprocess.run(args, stdout=stdout, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                print(result.stderr.strip())
        
        if stdout:
            stdout.close()
            
    except FileNotFoundError:
        print(f"{args[0]}: command not found")
    except PermissionError:
        print(f"{args[0]}: permission denied")
    except Exception as e:
        print(f"Error executing {args[0]}: {e}")

def execute_command(args, output_file=None, background=False):
    """Executa um comando (interno ou externo)"""
    if not args:
        return
    
    # Redirecionar saída se necessário (apenas para comandos internos)
    original_stdout = None
    if output_file and is_builtin(args[0]):
        try:
            original_stdout = sys.stdout
            sys.stdout = open(output_file, 'w', encoding='utf-8')
        except Exception as e:
            print(f"Error redirecting output: {e}")
            return
    
    try:
        # Tentar executar como comando interno
        if not execute_builtin(args):
            # Se não for interno, executar como externo
            execute_external(args, output_file, background)
    finally:
        # Restaurar stdout se foi redirecionado
        if original_stdout:
            sys.stdout.close()
            sys.stdout = original_stdout

def execute_parallel(command_line):
    """Executa comandos em paralelo (separados por &)"""
    commands = [cmd.strip() for cmd in command_line.split('&')]
    threads = []
    
    for i, cmd_str in enumerate(commands):
        if not cmd_str:
            continue
        
        args, output_file = parse_command(cmd_str)
        if not args:
            continue
        
        # Último comando não é background
        is_background = (i < len(commands) - 1)
        
        if is_builtin(args[0]):
            # Comandos internos executam na thread principal
            execute_command(args, output_file, is_background)
        else:
            # Comandos externos podem executar em background
            if is_background:
                thread = threading.Thread(
                    target=execute_external,
                    args=(args, output_file, True)
                )
                thread.start()
                threads.append(thread)
            else:
                execute_external(args, output_file, False)
    
    # Aguardar threads terminarem
    for thread in threads:
        thread.join()

def execute_sequential(command_line):
    """Executa comandos em sequência (separados por ;)"""
    commands = [cmd.strip() for cmd in command_line.split(';')]
    
    for cmd_str in commands:
        if not cmd_str:
            continue
        
        # Verificar se tem comandos paralelos
        if '&' in cmd_str:
            execute_parallel(cmd_str)
        else:
            args, output_file = parse_command(cmd_str)
            if args:
                execute_command(args, output_file)

def shell_loop():
    """Loop principal do shell"""
    global running
    
    print("Shell Simples em Python - Digite 'exit' para sair")
    
    while running:
        try:
            command_line = input("> ").strip()
            
            if not command_line:
                continue
            
            # Verificar tipo de comando
            if ';' in command_line:
                execute_sequential(command_line)
            elif '&' in command_line:
                execute_parallel(command_line)
            else:
                args, output_file = parse_command(command_line)
                if args:
                    execute_command(args, output_file)
                    
        except KeyboardInterrupt:
            print("\nUse 'exit' para sair")
        except EOFError:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

def main():
    """Função principal"""
    shell_loop()

if __name__ == "__main__":
    main()