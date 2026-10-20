-- =============================================================================
-- ESQUEMA DE MIGRACIÓN: SQLITE A SUPABASE (POSTGRESQL) CON RLS Y ROLES (RF-10)
-- Smurfit WestRock Colombia — Planta Industrial Yumbo
-- =============================================================================
-- Este script permite migrar la base de datos de prototipo (SQLite) directamente a
-- Supabase (PostgreSQL), habilitando Row Level Security (RLS) y control de acceso
-- por roles (Usuarios, Decisores, Diseñadores).
-- =============================================================================

-- 1. TABLA DE USUARIOS Y GOBERNANZA DE ACCESO (RF-10)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.usuarios (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    cargo VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Usuario', 'Decisor', 'Diseñador')),
    password_hash TEXT NOT NULL,
    salt VARCHAR(64) NOT NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMPTZ,
    ultimo_acceso TIMESTAMPTZ,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para optimizar búsquedas por email y verificación de bloqueos
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON public.usuarios(lower(email));
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON public.usuarios(rol);

-- 2. TABLA DE FACTORES DEL ENTORNO PESTEL (RF-01 a RF-06)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.factores (
    id BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    categoria_pestel VARCHAR(50) NOT NULL CHECK (
        categoria_pestel IN ('Político', 'Económico', 'Social', 'Tecnológico', 'Ecológico', 'Legal')
    ),
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Riesgo', 'Oportunidad')),
    ambito VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    probabilidad INT NOT NULL CHECK (probabilidad BETWEEN 1 AND 5),
    impacto INT NOT NULL CHECK (impacto BETWEEN 1 AND 5),
    urgencia VARCHAR(50) NOT NULL,
    puntuacion_severidad INT NOT NULL,
    prioridad_ponderada NUMERIC(5,2) NOT NULL,
    efecto_empresa TEXT NOT NULL,
    fuente_nombre VARCHAR(255) NOT NULL,
    fuente_url TEXT NOT NULL,
    fuente_confiabilidad VARCHAR(50) DEFAULT 'Alta',
    fecha_publicacion DATE NOT NULL,
    fecha_consulta DATE NOT NULL,
    estado VARCHAR(50) DEFAULT 'En Monitoreo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_factores_categoria ON public.factores(categoria_pestel);
CREATE INDEX IF NOT EXISTS idx_factores_tipo ON public.factores(tipo);
CREATE INDEX IF NOT EXISTS idx_factores_severidad ON public.factores(puntuacion_severidad DESC);

-- 3. TABLA DE HISTORIAL DE SEGUIMIENTO Y BITÁCORA (RF-08)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.historial_seguimiento (
    id BIGSERIAL PRIMARY KEY,
    factor_id BIGINT NOT NULL REFERENCES public.factores(id) ON DELETE CASCADE,
    fecha_registro TIMESTAMPTZ DEFAULT NOW(),
    observacion TEXT NOT NULL,
    usuario VARCHAR(255) DEFAULT 'Analista de Entorno',
    rol VARCHAR(50) DEFAULT 'Usuario' CHECK (rol IN ('Usuario', 'Decisor', 'Diseñador')),
    cambio_estado VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_historial_factor ON public.historial_seguimiento(factor_id);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON public.historial_seguimiento(fecha_registro DESC);

-- 4. TABLA DE RECOMENDACIONES ESTRATÉGICAS (RF-07)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.recomendaciones (
    id BIGSERIAL PRIMARY KEY,
    factor_id BIGINT NOT NULL REFERENCES public.factores(id) ON DELETE CASCADE,
    codigo_recomendacion VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    accion_sugerida TEXT NOT NULL,
    evidencia TEXT NOT NULL,
    prioridad VARCHAR(50) NOT NULL CHECK (prioridad IN ('Alta', 'Media', 'Baja')),
    area_responsable VARCHAR(100) NOT NULL,
    plazo VARCHAR(50) NOT NULL,
    estado VARCHAR(50) DEFAULT 'Planificada' CHECK (estado IN ('Planificada', 'En Ejecución', 'Completada')),
    autor_rol VARCHAR(50) DEFAULT 'Decisor',
    autor_nombre VARCHAR(255) DEFAULT 'Comité de Dirección'
);

CREATE INDEX IF NOT EXISTS idx_recomendaciones_factor ON public.recomendaciones(factor_id);
CREATE INDEX IF NOT EXISTS idx_recomendaciones_estado ON public.recomendaciones(estado);

-- -----------------------------------------------------------------------------
-- 5. TRIGGER DE ACTUALIZACIÓN AUTOMÁTICA DE 'updated_at'
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_usuarios_updated_at ON public.usuarios;
CREATE TRIGGER trigger_usuarios_updated_at
BEFORE UPDATE ON public.usuarios
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_factores_updated_at ON public.factores;
CREATE TRIGGER trigger_factores_updated_at
BEFORE UPDATE ON public.factores
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 6. POLÍTICAS DE ROW LEVEL SECURITY (RLS) EN SUPABASE
-- =============================================================================
-- Para activar seguridad a nivel de filas según el rol del JWT o perfil:

ALTER TABLE public.usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.factores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historial_seguimiento ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recomendaciones ENABLE ROW LEVEL SECURITY;

-- Función helper para obtener el rol del usuario autenticado en Supabase
CREATE OR REPLACE FUNCTION public.get_current_user_role()
RETURNS VARCHAR AS $$
    SELECT coalesce(
        current_setting('request.jwt.claims', true)::json->>'rol',
        (SELECT rol FROM public.usuarios WHERE email = current_setting('request.jwt.claims', true)::json->>'email')
    );
$$ LANGUAGE sql STABLE;

-- POLÍTICAS SOBRE 'factores':
-- Lectura: Todos los roles autenticados pueden consultar factores.
CREATE POLICY "factores_select_all"
ON public.factores FOR SELECT
TO authenticated, anon
USING (true);

-- Inserción / Edición / Eliminación: Exclusivo para Diseñador
CREATE POLICY "factores_insert_disenador"
ON public.factores FOR INSERT
TO authenticated
WITH CHECK (public.get_current_user_role() = 'Diseñador');

CREATE POLICY "factores_update_disenador_decisor"
ON public.factores FOR UPDATE
TO authenticated
USING (public.get_current_user_role() IN ('Diseñador', 'Decisor'));

CREATE POLICY "factores_delete_disenador"
ON public.factores FOR DELETE
TO authenticated
USING (public.get_current_user_role() = 'Diseñador');

-- POLÍTICAS SOBRE 'recomendaciones':
-- Lectura: Todos los roles pueden consultar el plan de acción.
CREATE POLICY "recomendaciones_select_all"
ON public.recomendaciones FOR SELECT
TO authenticated, anon
USING (true);

-- Inserción: Diseñador (sugerencias) y Decisor (aprobación)
CREATE POLICY "recomendaciones_insert_decisor_disenador"
ON public.recomendaciones FOR INSERT
TO authenticated
WITH CHECK (public.get_current_user_role() IN ('Decisor', 'Diseñador'));

-- Actualización de estado: Exclusivo para Decisor
CREATE POLICY "recomendaciones_update_decisor"
ON public.recomendaciones FOR UPDATE
TO authenticated
USING (public.get_current_user_role() = 'Decisor');

-- POLÍTICAS SOBRE 'historial_seguimiento':
-- Lectura e inserción abierta para cualquier usuario autenticado
CREATE POLICY "historial_select_all"
ON public.historial_seguimiento FOR SELECT
TO authenticated, anon
USING (true);

CREATE POLICY "historial_insert_authenticated"
ON public.historial_seguimiento FOR INSERT
TO authenticated
WITH CHECK (true);

-- =============================================================================
-- 7. DATOS SEMILLA DE USUARIOS INICIALES (MISMOS QUE EL PROTOTIPO SQLITE)
-- =============================================================================
-- Contraseñas hasheadas con PBKDF2-HMAC-SHA256 (100.000 iteraciones):
-- - Diseñador: Disenador2026*
-- - Decisor:   Decisor2026*
-- - Usuario:   Usuario2026*
-- =============================================================================
INSERT INTO public.usuarios (email, nombre, cargo, rol, password_hash, salt, intentos_fallidos, activo)
VALUES
('disenador@smurfitwestrock.com', 'Ing. Sofía Ramírez', 'Especialista en Inteligencia Competitiva & PESTEL', 'Diseñador',
 'eff1059e2dccaf83f2a8ef64c51480436ce02d0cfd68fcf9a224a13d968565b3', '3f23a5cf804d9a44fb17eb04cd76662e', 0, TRUE),
('decisor@smurfitwestrock.com', 'Dr. Carlos Mendoza', 'Director General de Operaciones & Estrategia Yumbo', 'Decisor',
 'cb45f7fbab69fc7345b1285038ec8b449bca7e8e1215469fa7788448ebf5c8d6', '8b48873fb2a91f422c54f5aa17df66cf', 0, TRUE),
('usuario@smurfitwestrock.com', 'Laura Gómez', 'Analista de Monitoreo & Operaciones de Planta', 'Usuario',
 '5c7ccc730103c94b79c3227497ec02476b7e53f53856cb4b256fa0d1a457199c', 'c381c828d54203ae043d9bf3c965e638', 0, TRUE)
ON CONFLICT (email) DO NOTHING;
