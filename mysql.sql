-- Tabla de roles de usuario
CREATE TABLE Usu_rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla de cursos
CREATE TABLE Cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    duracion INT, -- en horas, por ejemplo
    disponibilidad BOOLEAN DEFAULT TRUE
);

-- Tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT ,
    tipo VARCHAR(50),
    nombre VARCHAR(100) ,
    apellido VARCHAR(100) ,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) ,
    fecha_creacion DATETIME ,
    fecha_mod DATETIME ,
    habilitado BOOLEAN ,
    FOREIGN KEY (id_rol) REFERENCES usu_rol(id)
);

-- Tabla sesiones
CREATE TABLE user_sessions (
    id          INT NOT NULL AUTO_INCREMENT,
    id_user     INT NOT NULL,
    fecha_login DATETIME DEFAULT NULL,
    PRIMARY KEY (id)
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci;

-- Tabla usuarios cursos
CREATE TABLE usuarios_cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    curso_id INT,
    fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);


INSERT INTO cursos (nombre, descripcion, duracion, disponibilidad) VALUES
('Python desde Cero', 'Curso para aprender los fundamentos de Python. Recomendado para principiantes.', 40, TRUE),
('Flask Web Framework', 'Desarrolla aplicaciones web modernas con Flask y Python.', 30, TRUE),
('Machine Learning Básico', 'Introducción a los modelos de aprendizaje automático. No requiere experiencia previa.', 50, TRUE),
('Bases de Datos con MySQL', 'Aprende a diseñar y consultar bases de datos relacionales con SQL.', 25, TRUE);
