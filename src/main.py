import sqlite3
import os

# --- CONFIGURAZIONE DATABASE ---

def connect_db():
    """Stabilisce la connessione al database e abilita i vincoli delle chiavi esterne."""
    conn = sqlite3.connect('gestione_spese.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inizializza_database():
    """Crea le tabelle necessarie se non sono già presenti nel sistema."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # 1. Tabella Categorie (Modulo 1)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Categorie (
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
    )''')
    
    # 2. Tabella Spese (Modulo 2)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Spese (
        id_spesa INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL CHECK(data LIKE '____-__-__'),
        importo REAL NOT NULL CHECK(importo > 0),
        descrizione TEXT,
        id_categoria INTEGER NOT NULL,
        FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
    )''')
    
    # 3. Tabella Budget (Modulo 3)
    cursor.execute('''CREATE TABLE IF NOT EXISTS Budget (
        id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
        mese TEXT NOT NULL CHECK(mese LIKE '____-__'),
        importo_limite REAL NOT NULL CHECK(importo_limite > 0),
        id_categoria INTEGER NOT NULL,
        UNIQUE(mese, id_categoria),
        FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
    )''')
    
    conn.commit()
    conn.close()

# --- LOGICA DEI MODULI (INPUT -> ELABORAZIONE -> OUTPUT) ---

def gestione_categorie():
    """MODULO 1: Consente di definire nuove categorie di spesa."""
    print("\n--- GESTIONE CATEGORIE ---")
    nome = input("Inserisci il nome della categoria (es. Alimentari): ").strip()
    
    if not nome:
        print("Errore: Il nome della categoria non può essere vuoto.")
        return

    conn = connect_db()
    try:
        conn.execute("INSERT INTO Categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("Successo: Categoria inserita correttamente.")
    except sqlite3.IntegrityError:
        print("Errore: La categoria esiste già.")
    finally:
        conn.close()

def inserisci_spesa():
    """MODULO 2: Registra una nuova transazione di spesa."""
    print("\n--- INSERIMENTO NUOVA SPESA ---")
    data = input("Inserisci la data (formato YYYY-MM-DD): ").strip()
    
    try:
        importo = float(input("Inserisci l'importo: "))
        if importo <= 0:
            print("Errore: L'importo deve essere maggiore di zero.")
            return
    except ValueError:
        print("Errore: Inserire un numero valido per l'importo.")
        return

    cat_nome = input("Inserisci il nome della categoria: ").strip()
    descrizione = input("Inserisci una descrizione (facoltativa): ").strip()

    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_categoria FROM Categorie WHERE nome = ?", (cat_nome,))
    res = cursor.fetchone()

    if res:
        cursor.execute("INSERT INTO Spese (data, importo, descrizione, id_categoria) VALUES (?, ?, ?, ?)",
                       (data, importo, descrizione, res[0]))
        conn.commit()
        print("Successo: Spesa inserita correttamente.")
    else:
        print("Errore: La categoria non esiste. Creala prima nel Modulo 1.")
    conn.close()

def definisci_budget():
    """MODULO 3: Imposta un limite di spesa mensile per una categoria."""
    print("\n--- DEFINIZIONE BUDGET MENSILE ---")
    mese = input("Inserisci il mese (formato YYYY-MM): ").strip()
    
    try:
        importo = float(input("Inserisci l'importo del budget: "))
        if importo <= 0:
            print("Errore: Il budget deve essere maggiore di zero.")
            return
    except ValueError:
        print("Errore: Inserire un numero valido per il budget.")
        return

    cat_nome = input("Inserisci il nome della categoria: ").strip()

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_categoria FROM Categorie WHERE nome = ?", (cat_nome,))
    res = cursor.fetchone()

    if res:
        cursor.execute("INSERT OR REPLACE INTO Budget (mese, importo_limite, id_categoria) VALUES (?, ?, ?)",
                       (mese, importo, res[0]))
        conn.commit()
        print(f"Successo: Budget mensile per '{cat_nome}' salvato correttamente.")
    else:
        print("Errore: La categoria non esiste.")
    conn.close()

def visualizza_report():
    """MODULO 4: Sottomenu per la visualizzazione dei report calcolati."""
    while True:
        print("\n" + "="*25)
        print("      MENU REPORT")
        print("="*25)
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo spese (per data)")
        print("4. Ritorna al menu principale")
        
        scelta = input("\nInserisci la tua scelta: ")
        conn = connect_db()
        cursor = conn.cursor()

        if scelta == '1':
            print("\nREPORT 1: TOTALE SPESE PER CATEGORIA")
            cursor.execute("""SELECT c.nome, SUM(s.importo) 
                              FROM Spese s JOIN Categorie c ON s.id_categoria = c.id_categoria 
                              GROUP BY c.nome""")
            print("Categoria........Totale Speso")
            for r in cursor.fetchall():
                print(f"{r[0]:<17} {r[1]:>12.2f}")
        
        elif scelta == '2':
            print("\nREPORT 2: SPESE MENSILI VS BUDGET")
            cursor.execute("""
                SELECT b.mese, c.nome, b.importo_limite, IFNULL(SUM(s.importo), 0)
                FROM Budget b
                JOIN Categorie c ON b.id_categoria = c.id_categoria
                LEFT JOIN Spese s ON b.id_categoria = s.id_categoria 
                    AND strftime('%Y-%m', s.data) = b.mese
                GROUP BY b.id_budget
            """)
            for r in cursor.fetchall():
                mese, cat, budget, speso = r
                stato = "SUPERAMENTO BUDGET" if speso > budget else "OK"
                print(f"\nMese: {mese}\nCategoria: {cat}\nBudget: {budget} | Speso: {speso}\nStato: {stato}")
        
        elif scelta == '3':
            print("\nREPORT 3: ELENCO COMPLETO DELLE SPESE")
            cursor.execute("""SELECT s.data, c.nome, s.importo, s.descrizione 
                              FROM Spese s JOIN Categorie c ON s.id_categoria = c.id_categoria 
                              ORDER BY s.data DESC""")
            print(f"{'Data':<12} {'Categoria':<15} {'Importo':<10} {'Descrizione'}")
            print("-" * 60)
            for r in cursor.fetchall():
                print(f"{r[0]:<12} {r[1]:<15} {r[2]:<10.2f} {r[3]}")
        
        elif scelta == '4':
            conn.close()
            break
        else:
            print("Scelta non valida. Riprovare.")
        conn.close()

# --- CICLO ITERATIVO PRINCIPALE (MODIFICATO SECONDO REQUISITI) ---

def main():
    # Inizializzazione del Database
    inizializza_database()
    
    # 1. MESSAGGIO DI BENVENUTO (Punto 3.1)
    print("========================================")
    print("   BENVENUTO NEL SISTEMA DI GESTIONE    ")
    print("       SPESE PERSONALI E BUDGET         ")
    print("========================================")
    
    # CICLO ITERATIVO per ripetere il menu (Punto 4)
    while True:
        # 2. MOSTRA IL MENU PRINCIPALE (Punto 3.2 e 4 - cout equivalent)
        print("\n-------------------------")
        print(" SISTEMA SPESE PERSONALI ")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")
        
        # 3. ATTENDERE LA SCELTA DELL'UTENTE (Punto 3.3 e 4 - cin equivalent)
        scelta = input("Inserisci la tua scelta: ")

        # 4. LOGICA DEL MENU / SELEZIONE (Punto 5 - switch equivalent)
        if scelta == '1':
            gestione_categorie()
        elif scelta == '2':
            inserisci_spesa()
        elif scelta == '3':
            definisci_budget()
        elif scelta == '4':
            visualizza_report()
        elif scelta == '5':
            # Uscita programmata
            print("\nUscita dal sistema. Arrivederci!")
            break 
        else:
            # Validazione scelta (Punto 5)
            print("\nScelta non valida. Riprovare.")

if __name__ == "__main__":
    main()
