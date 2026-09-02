-- Script de inicialización de la base de datos MiFicha
-- Este archivo se ejecuta automáticamente al iniciar el contenedor PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabla para Personas
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100) NOT NULL,
    numero_carnet VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    tipo_persona VARCHAR(50) NOT NULL DEFAULT 'solicitante',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_persona CHECK (tipo_persona IN ('solicitante', 'profesional', 'admin'))
);

-- Tabla para Dispositivos Móviles
CREATE TABLE dispositivos_moviles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    android_id VARCHAR(255) UNIQUE NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Cuentas
CREATE TABLE cuentas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    persona_id UUID NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    dispositivo_id UUID REFERENCES dispositivos_moviles(id) ON DELETE SET NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_autenticacion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_cuentas_correo ON cuentas(correo);
CREATE INDEX idx_cuentas_persona_id ON cuentas(persona_id);
CREATE INDEX idx_cuentas_dispositivo_id ON cuentas(dispositivo_id);
CREATE INDEX idx_personas_numero_carnet ON personas(numero_carnet);
CREATE INDEX idx_dispositivos_android_id ON dispositivos_moviles(android_id);

-- Crear tabla de auditoría (para logging)
CREATE TABLE auditoria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabla VARCHAR(100) NOT NULL,
    operacion VARCHAR(50) NOT NULL,
    registro_id UUID NOT NULL,
    usuario_id UUID,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE INDEX idx_auditoria_timestamp ON auditoria(timestamp);
CREATE INDEX idx_auditoria_tabla ON auditoria(tabla);

-- Comentarios de documentación
COMMENT ON TABLE personas IS 'Almacena información de personas del sistema';
COMMENT ON TABLE dispositivos_moviles IS 'Almacena información de dispositivos móviles registrados';
COMMENT ON TABLE cuentas IS 'Almacena cuentas de usuario con sus credenciales';
COMMENT ON TABLE auditoria IS 'Registro de auditoría de cambios en la base de datos';

-- Grant de permisos al usuario de la aplicación
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mificha_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mificha_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO mificha_user;
