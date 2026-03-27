#john2.1.py
import os
import subprocess

def win_to_wsl(path):
    path = os.path.abspath(path) # Converti in percorso assoluto
    path = path.replace("\\", "/") # Sostituisci backslash con slash
    if ":" in path:
        drive = path[0].lower() # Prendi la lettera dell'unità e converti in minuscolo
        path = f"/mnt/{drive}{path[2:]}" # Sostituisci "C:" con "/mnt/c", 2: è per rimuovere "C:"
    return path


def ask_wordlist():
    while True:
        file = input("Inserire la wordlist: ")
        if os.path.exists(file):
            wsl_path = win_to_wsl(file)
            nome = os.path.basename(file) # Ottieni solo il nome del file senza il percorso

            subprocess.run([
                "wsl", "bash", "-c",
                f"cd ~/john-jumbo/run && cp '{wsl_path}' '{nome}'"
            ], check=True) #check=True per sollevare un'eccezione se il comando fallisce

            return nome
        else:
            print("File non esiste")


def richiesta():
    while True:
        file = input("Inserire il file da crackare: ")
        if os.path.exists(file):
            wsl_path = win_to_wsl(file)
            nome = os.path.basename(file)

            subprocess.run([
                "wsl", "bash", "-c",
                f"cd ~/john-jumbo/run && cp '{wsl_path}' '{nome}'"
            ], check=True)

            return nome
        else:
            print("File non esiste")


def Personalizzazione():
    C = input("Conosci qualcosa della password? (S/N)")

    if C.lower() == "s":
        while True:
            n = input("Numeri, Lettere o ASCII? (N/L/A): ")
            if n.lower() in ("n", "l", "a"):
                break

        if n.lower() == "n":
            q = input("Conosci lunghezza? (S/N): ")
            if q.lower() == "s":
                l = int(input("Lunghezza: "))
                return "--mask=" + "?d" * l
            else:
                return "--incremental=Digits"

        elif n.lower() == "l":
            q = input("Conosci lunghezza? (S/N): ")
            if q.lower() == "s":
                l = int(input("Lunghezza: "))
                return "--mask=" + "?1" * l + " --1=[a-zA-Z]"
            else:
                return "--incremental=Alpha"

        elif n.lower() == "a":
            q = input("Conosci lunghezza? (S/N): ")
            if q.lower() == "s":
                l = int(input("Lunghezza: "))
                return "--mask=" + "?a" * l
            else:
                return "--incremental=ASCII"

    return "--incremental"


def scegli_tipo():
    tipi = {
        "1": "7z2john.pl",
        "2": "zip2john",
        "3": "rar2john",
        "4": "pdf2john.pl",
        "5": "office2john.py",
        "6": "gpg2john",
        "7": "truecrypt2john.py"
    }

    while True:
        print("1 7z | 2 ZIP | 3 RAR | 4 PDF | 5 Office | 6 GPG | 7 TRUECRYPT")
        t = input("Tipo: ")
        if t in tipi:
            return tipi[t]


def esecuzione(file, wordlist, opzioni):
    TIPO = scegli_tipo()
    hashfile = file + ".hash"

    base = "cd ~/john-jumbo/run && "

    # genera hash
    if TIPO.endswith(".pl"):
        cmd_hash = f"{base} perl {TIPO} {file} > {hashfile}"
    elif TIPO.endswith(".py"):
        cmd_hash = f"{base} python3 {TIPO} {file} > {hashfile}"
    else:
        cmd_hash = f"{base} ./{TIPO} {file} > {hashfile}"
    subprocess.run(["wsl", "bash", "-c", cmd_hash], check=True)
    
   

    # prova wordlist
    try:
        cmd_john = f"{base} ./john --wordlist={wordlist} --rules {hashfile} > /dev/null 2>&1" # reindirizza output e errori a /dev/null, ossia li ignora
        subprocess.run(["wsl", "bash", "-c", cmd_john], timeout=900, check=True)
    except subprocess.TimeoutExpired:
     #wordlist fallsca, passo a brute force
        print("Timeout → brute force")
        cmd_brute = f"{base} ./john {opzioni} {hashfile}"
        subprocess.run(["wsl", "bash", "-c", cmd_brute], check=True)

    # mostra risultato
    show_cmd = f"{base} ./john --show {hashfile}"
    result = subprocess.run(["wsl", "bash", "-c", show_cmd],
                            capture_output=True, text=True)

    print(result.stdout)

    # pulizia
    cleanup = f"{base} rm -f {file} {hashfile}"
    subprocess.run(["wsl", "bash", "-c", cleanup])


# MAIN
wordlist = ask_wordlist()
file = richiesta()
opzioni = Personalizzazione()
esecuzione(file, wordlist, opzioni)
