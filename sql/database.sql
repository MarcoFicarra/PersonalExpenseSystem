-- ======================================================
-- SCHEMA DEL DATABASE E VINCOLI DI INTEGRITÀ
-- ======================================================

-- 1. Tabella Categorie: Anagrafica delle tipologie di spesa
CREATE TABLE Categorie (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,        -- [PRIMARY KEY]
    nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)      -- [NOT NULL], [UNIQUE], [CHECK]
);

-- 2. Tabella Spese: Registro delle transazioni effettuate
CREATE TABLE Spese (
    id_spesa INTEGER PRIMARY KEY AUTOINCREMENT,            -- [PRIMARY KEY]
    data TEXT NOT NULL CHECK(data LIKE '____-__-__'),      -- [NOT NULL], [CHECK] (Formato YYYY-MM-DD)
    importo REAL NOT NULL CHECK(importo > 0),              -- [NOT NULL], [CHECK] (Valore positivo)
    descrizione TEXT,
    id_categoria INTEGER NOT NULL,                         -- [NOT NULL]
    -- [FOREIGN KEY] Vincolo di integrità referenziale verso la tabella Categorie
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
);

-- 3. Tabella Budget: Pianificazione dei tetti di spesa mensili
CREATE TABLE Budget (
    id_budget INTEGER PRIMARY KEY AUTOINCREMENT,            -- [PRIMARY KEY]
    mese TEXT NOT NULL CHECK(mese LIKE '____-__'),          -- [NOT NULL], [CHECK] (Vincolo Formato YYYY-MM)
    importo_limite REAL NOT NULL CHECK(importo_limite > 0), -- [NOT NULL], [CHECK]
    id_categoria INTEGER NOT NULL,                          -- [NOT NULL]
    -- [UNIQUE] Vincolo composto: impedisce duplicati per la stessa categoria nello stesso mese
    UNIQUE(mese, id_categoria),
    -- [FOREIGN KEY] Vincolo di integrità referenziale verso la tabella Categorie
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
);

-- ======================================================
-- INSERIMENTO DATI DI ESEMPIO (TEST FUNZIONALE)
-- ======================================================

-- Popolamento delle categorie (Verifica vincolo UNIQUE)
INSERT INTO Categorie (nome) VALUES ('Alimentari'), ('Trasporti'), ('Affitto');

-- Registrazione Spese (Verifica vincolo FOREIGN KEY e formato data)
INSERT INTO Spese (data, importo, descrizione, id_categoria) 
VALUES ('2026-01-08', 55.20, 'Spesa supermercato', 1),
       ('2026-01-08', 20.00, 'Rifornimento carburante', 2);

-- Definizione Budget per Gennaio 2026 (Verifica vincolo CHECK e NOT NULL)
INSERT INTO Budget (mese, importo_limite, id_categoria) 
VALUES ('2026-01', 400.00, 1),
       ('2026-01', 100.00, 2);
