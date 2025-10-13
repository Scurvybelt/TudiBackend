-- Crear tabla de fases del curso
CREATE TABLE IF NOT EXISTS course_phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    phase_order INTEGER UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de progreso del usuario en el curso
CREATE TABLE IF NOT EXISTS user_course_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    phase_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'locked' CHECK (status IN ('locked', 'available', 'in_progress', 'completed')),
    started_at DATETIME,
    completed_at DATETIME,
    progress_percentage REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES course_phases (id) ON DELETE CASCADE,
    UNIQUE(user_id, phase_id)
);

-- Insertar fases iniciales del curso
INSERT OR IGNORE INTO course_phases (name, description, phase_order) VALUES
('Fase 1', 'Primer Contacto', 1),
('Fase 2', 'La estrategia', 2),
('Fase 3', 'La conceptualización', 3),
('Fase 4', 'Desarrollo de proyecto', 4),
('Fase 5', 'Testeo de la propuesta', 5),
('Fase 6', 'Presenta la propuesta', 6),
('Fase 7', 'Cierre del proyecto', 7);