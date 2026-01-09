-- 1. CREAZIONE TABELLE CON VINCOLI ESPLICITI
CREATE TABLE Categorie (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE CHECK(length(nome) > 0)
);

CREATE TABLE Spese (
    id_spesa INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL CHECK(data LIKE '____-__-__'), -- Vincolo formato YYYY-MM-DD
    importo REAL NOT NULL CHECK(importo > 0),        -- Vincolo CHECK importo positivo
    descrizione TEXT,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
);

CREATE TABLE Budget (
    id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
    mese TEXT NOT NULL CHECK(mese LIKE '____-__'),    -- Vincolo formato YYYY-MM
    importo_limite REAL NOT NULL CHECK(importo_limite > 0),
    id_categoria INTEGER NOT NULL,
    UNIQUE(mese, id_categoria),                      -- Vincolo UNIQUE (Integrità)
    FOREIGN KEY (id_categoria) REFERENCES Categorie(id_categoria) ON DELETE CASCADE
);

-- 2. INSERIMENTO DATI DI ESEMPIO
INSERT INTO Categorie (nome) VALUES ('Alimentari'), ('Trasporti'), ('Affitto');

INSERT INTO Spese (data, importo, descrizione, id_categoria) 
VALUES ('2026-01-08', 55.20, 'Spesa supermercato', 1),
       ('2026-01-08', 20.00, 'Rifornimento carburante', 2);

INSERT INTO Budget (mese, importo_limite, id_categoria) 
VALUES ('2026-01', 400.00, 1),
       ('2026-01', 100.00, 2);