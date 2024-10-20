import sqlite3

# Connessione al database
conn = sqlite3.connect('user_ips.db')
c = conn.cursor()

# Crea la tabella per gli IP
c.execute('''CREATE TABLE IF NOT EXISTS ips (
    user_id INTEGER PRIMARY KEY,
    ip_address TEXT
)''')

# Salva le modifiche e chiudi la connessione
conn.commit()
conn.close()
