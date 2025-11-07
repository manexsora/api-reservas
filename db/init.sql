CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NULL,
    password TEXT NOT NULL,  
    email TEXT NULL
);

CREATE TABLE IF NOT EXISTS courts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_zona TEXT NOT NULL,           
    id_actividad_libre TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           
    user_id INTEGER NOT NULL,     
    court_id INTEGER NOT NULL,    
    
    reservation_day TEXT NOT NULL, 
    reservation_time TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,   
    
    -- Restricciones de Clave Foránea
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (court_id) REFERENCES courts (id) ON DELETE CASCADE
);