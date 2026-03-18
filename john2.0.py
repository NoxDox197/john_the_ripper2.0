# jhon 2.0
import os
import subprocess
import shlex


# chiedo di inserire il file
def richiesta():

    while True:
        file = input(
            "Inserire il nome del file di cui trovare la password: (é preferibile rinominare il file con un nome semplice senza spazi o caratteri speciali) "
        )
        if os.path.exists(file):
            return file
        else:
            print("il file non esiste")


def controllo(proc):
    if proc.returncode == 0:
        print("Processo eseguito")
    else:
        print("Errore")
        print(proc.stderr)


file = richiesta()
file_safe = shlex.quote(file)
hashfile = file + ".hash"
hash_safe = shlex.quote(hashfile)
percorso = os.path.abspath(file)
percorso_wsl = percorso.replace("C:\\", "/mnt/c/").replace("\\", "/")
path_safe = shlex.quote(percorso_wsl)


def Personalizzazione():

    C = input("Conosci qualcosa della password? (S/N)")
    if C.lower() == "s":
        n = input(
            "La password ha solo numeri o lettere o caratteri stampabili ASCII? (N/L/A)"
        )
        # numeri
        if n.lower() == "n":
            qn = input(
                "Conosci la lunghezza della password? (S/N)"
            )  # qn = quantita numeri
            if qn.lower() == "s":
                lunghezza = input("Inserire la lunghezza della password: ")
                print(f"La password ha {lunghezza} caratteri")
                opzioni = "--mask=" + ("?" + "d") * int(lunghezza)
                print(f"la maschera da usare è: {opzioni}")
            else:
                print("La password ha solo numeri ma non conosci la lunghezza")
                opzioni = "--incremental=Digits "

        # lettere
        elif n.lower() == "l":
            ql = input(
                "Conosci la lunghezza della password? (S/N)"
            )  # ql = quantita lettere
            if ql.lower() == "s":
                lunghezza = input("Inserire la lunghezza della password: ")
                print(f"La password ha {lunghezza} caratteri")
                opzioni = "--mask=" + (("?" + "1") * int(lunghezza)) + " --1=[a-zA-Z]"
                print(f"la maschera da usare è: {opzioni}")
            else:
                print("La password ha solo lettere ma non conosci la lunghezza")
                opzioni = "--incremental=Alpha "

        # ASCII
        elif n.lower() == "a":
            ql = input(
                "Conosci la lunghezza della password? (S/N)"
            )  # ql = quantita lettere
            if ql.lower() == "s":
                lunghezza = input("Inserire la lunghezza della password: ")
                print(f"La password ha {lunghezza} caratteri")
                opzioni = "--mask=" + ("?" + "a") * int(lunghezza)
                print(f"la maschera da usare è: {opzioni}")
            else:
                print(
                    "La password ha solo caratteri stampabili ASCII ma non conosci la lunghezza"
                )
                opzioni = "--incremental=ASCII "
    else:
        opzioni = "--incremental "
    return opzioni


opzioni = Personalizzazione()


# determino il comando da eseguire e lo eseguo
def esecuzione():

    # tipo di file
    print(
        "Inserire il tipo di file tra quelli supportati: " + "\n"
        "1 -> 7z" + "\n"
        "2 -> ZIP" + "\n"
        "3 -> RAR" + "\n"
        "4 -> PDF" + "\n"
        "5 -> Office( DOC/DOCX, XLS/XLSX, PPT/PPTX)" + "\n"
        "6 -> GPG / OpenPGP" + "\n"
        "7 -> TRUECRYPT / VERACRYPT" + "\n"
    )
    while True:

        T = input("Che tipo di file è? ")

        if T == "1":
            TIPO = "7z2john"
            break
        elif T == "2":
            TIPO = "zip2john"
            break
        elif T == "3":
            TIPO = "rar2john"
            break
        elif T == "4":
            TIPO = "pdf2john"
            break
        elif T == "5":
            TIPO = "office2john"
            break
        elif T == "6":
            TIPO = "gpg2john"
            break
        elif T == "7":
            TIPO = "truecrypt2john"
            break
        else:
            print("Tipo di file non supportato, prova con uno nella lista")

    # i comandi

    cmd_cp = ["wsl", "bash", "-c", f"cd ~/john-jumbo/run && cp {path_safe} ."]

    cmd_hash = [
        "wsl",
        "bash",
        "-c",
        f"cd ~/john-jumbo/run && ./{TIPO} {file_safe} > {hash_safe}",
    ]
    cmd_john = [
        "wsl",
        "bash",
        "-c",
        f"cd ~/john-jumbo/run && ./john --wordlist=... --rules {hash_safe}",
    ]

    # cmd_cp: copio il file da craccare nella cartella di john

    # lo eseguo con i vai accorgmenti per avere output chiaro e usare la shell
    process = subprocess.run(cmd_cp, capture_output=True, text=True)
    controllo(process)
    if process.returncode != 0:
        return

    # cmd_hash: genero l'hash del file da craccare

    process = subprocess.run(
        cmd_hash,
        capture_output=True,
        text=True,
    )
    controllo(process)
    if process.returncode != 0:
        return

    # COMANDO3: eseguo john sul file hash
    try:
        process = subprocess.run(cmd_john, capture_output=True, text=True, timeout=300)
        controllo(process)
        if process.returncode != 0:
            return
    except subprocess.TimeoutExpired:
        print("Il processo ha impiegato troppo tempo e è stato terminato.")

        cmd_brute = [
            "wsl",
            "bash",
            "-c",
            f"cd ~/john-jumbo/run && ./john {opzioni} {hash_safe}",
        ]
        # copia file
        process = subprocess.run(
            cmd_brute,
            capture_output=True,
            text=True,
        )

    # controllo se tutto è andato bene e stampo l'output
    if process.returncode == 0:
        print("Processo eseguito")

    else:
        print("Errore nell'avvio del processo")
        print(process.stderr)


esecuzione()


def pulizia():
    # elimino i file creati

    cmd_rm_hash = ["wsl", "bash", "-c", f"cd ~/john-jumbo/run && rm -f {hash_safe}"]

    cmd_rm_file = ["wsl", "bash", "-c", f"cd ~/john-jumbo/run && rm -f {file_safe}"]

    subprocess.run(cmd_rm_hash)
    subprocess.run(cmd_rm_file)


show_cmd = ["wsl", "bash", "-c", f"cd ~/john-jumbo/run && ./john --show {hash_safe}"]
show = subprocess.run(
    show_cmd,
    capture_output=True,
    text=True,
)

print(show.stdout)



pulizia()
