import shlex #parsing de comandos
import subprocess
import concurrent.futures
import contextlib  # Para redirecionar a saída
import os
import sys

running = True

# divir o comando em partes para analisar depois
def dividir_comando(comando):
    comando=comando.strip()
    tokens=shlex.split(comando)
    args=[]
    out_file=[]
    for i in range (len(tokens)):
        if tokens[i] != ">":
            args.append(tokens[i])
        else:
            for j in range (i,len(tokens)):
                out_file.append(tokens[j])
            return args,out_file
    return args,None


#pwd - exibe o caminho do diretorio atual
def cmd_pwd():
    print(os.getcwd())

#cd - muda o diretorio autal (change diretory)
def cmd_cd(args):
    if len(args) != 2:
        # Sem argumentos ou mais de um argumento - não faz nada
        print("argumentos faltantes ou invalidos")
        return

    try:
        os.chdir(args[1])
        print("diretorio trocado > ",args[1])
    except (FileNotFoundError, NotADirectoryError):
        print("diretório não encontrado")
    except PermissionError:
        print("sem permição para acessar esse arquivo")


#cat - exibe o conteudo de um arquivo
def cmd_cat(args):
    if len(args) < 2:
        print("argumentos faltantes ou inválidos")
        return

    for filename in args[1:]:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                print(file.read(), end='')
        except FileNotFoundError:
            print(f"cat: {filename}: arquivo não encontrado")
        except PermissionError:
            print(f"cat: {filename}: permissão negada")
        except UnicodeDecodeError:
            try:
                # Tentar com codificação latin-1 se UTF-8 falhar
                with open(filename, 'r', encoding='latin-1') as file:
                    print(file.read(), end='')
            except Exception:
                print(f"cat: {filename}: não foi possível ler o arquivo")


#ls - lista conteudo do diretório atual
def cmd_ls():
    try:
        entries = []
        for item in os.listdir('.'):
            if not item.startswith('.'):  # Não mostrar arquivos ocultos
                entries.append(item)

        entries.sort()
        for entry in entries:
            print("\n",entry, end='  ')
        if entries:
            print()  # Nova linha no final
    except PermissionError:
        print("ls: permissão negada")


#echo - imprime texto na tela
def cmd_echo(args):
    if len(args) > 1:
        print(' '.join(args[1:]))
    else:
        print()

#selecionar qual comando vai executar
def commands(args):
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

# Para executar comandos sequencialmente
def execute_sequential(command_line):
    commands = command_line.split(';')
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            print(f"[Sequencial] Executando: {cmd}")
            args, output_file = dividir_comando(cmd)
            if args:
                execute_command(args, output_file)

# Para executar comandos em paralelo
def execute_parallel(command_line):
    commands = command_line.split('&')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:
                print(f"[Paralelo] Agendado: {cmd}")
                args, output_file = dividir_comando(cmd)
                if args:
                    future = executor.submit(execute_command, args, output_file)
                    futures.append(future)
        
        # Aguarda todos os comandos terminarem
        concurrent.futures.wait(futures)

def execute_command(args, output_file=None):
    if not args:
        return

    # Redirecionar saída se necessário (apenas para comandos internos)
    try:
        if output_file:
            with open(output_file[1], 'w', encoding='utf-8') as f:
                with contextlib.redirect_stdout(f):
                    commands(args)
            print(f"[Redirecionamento] Saída salva em: {output_file[1]}")
        else:
            commands(args)

    except Exception as e:
        print(f"Erro ao executar comando: {e}")


# loop do terminal
def loop_terminal():
    global running

    print("Shell Simples em Python - Digite 'exit' para sair")

    while running:
        try:
            command_line = input("\n> ").strip()

            if not command_line:
                continue

             # Verifica se há comandos sequenciais ou paralelos
            if ';' in command_line:
                execute_sequential(command_line)

            elif '&' in command_line:
                execute_parallel(command_line)

            else:
                args, output_file = dividir_comando(command_line)
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
    loop_terminal()

if __name__ == "__main__":
    main()
