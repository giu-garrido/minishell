# CMD Python

**Como iniciar**

1. Certifique-se de que você tem o Python instalado.

2. Salve o script com o nome `shell.py` (ou outro de sua escolha).

3. Execute no terminal ou prompt de comando com:

```bash
python shell.py
```

Você verá:

```
Shell Simples em Python - Digite 'exit' para sair
>
```

---

**Comandos suportados**

- `pwd`  
Mostra o caminho do diretório atual.

```bash
> pwd
/home/user
```

- `cd <caminho>`  
Muda o diretório atual.

```bash
> cd pasta
> pwd
/home/user/pasta
```

Se o caminho for inválido:

```
diretório não encontrado
```

- `ls`  
Lista os arquivos e pastas do diretório atual.

```bash
> ls
arquivo.txt  pasta1  script.py
```

- `cat <arquivo>`  
Mostra o conteúdo de um ou mais arquivos.

```bash
> cat texto.txt
Olá, mundo!
```

- `echo <texto>`  
Imprime o texto na tela.

```bash
> echo Testando...
Testando...
```

- `exit`  
Sai do shell.

```bash
> exit
```

---

**Funcionalidades extras**

**Redirecionamento de saída**  
Você pode enviar a saída de um comando para um arquivo usando `>`:

```bash
> echo Olá > saudacao.txt
```

Isso salva `Olá` dentro do arquivo `saudacao.txt`.

**Execução em paralelo com `&`**  
Comandos separados por `&` serão executados ao mesmo tempo:

```bash
> echo A > a.txt & echo B > b.txt
```

Isso executa os dois comandos simultaneamente e salva as saídas nos respectivos arquivos.

Você verá mensagens como:

```
[Paralelo] Agendado: echo A > a.txt
[Paralelo] Iniciando: echo A
[Redirecionamento] Saída salva em: a.txt
```

**Execução em sequência com `;`**  
Comandos separados por `;` serão executados um de cada vez, na ordem:

```bash
> echo primeiro ; echo segundo ; echo terceiro
```

Você verá:

```
[Sequencial] Executando: echo primeiro
primeiro
[Sequencial] Executando: echo segundo
segundo
[Sequencial] Executando: echo terceiro
terceiro
```

---

**Observações importantes**

- Os comandos precisam estar separados por espaço.
- O `cd` não faz nada se for usado sem caminho ou com muitos argumentos.
- Arquivos ou pastas ocultos (começando com `.`) não aparecem no `ls`.
- O terminal mostra mensagens para ajudar a entender se algo falhou.
