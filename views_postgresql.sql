-- ============================================================
-- Views para PostgreSQL - Convertidas do MySQL
-- Banco: Unico_Database
-- Data: 06/02/2026
-- ============================================================

-- Nota: Execute este arquivo APÓS a migração com pgloader
-- Use: psql -U postgres -d Unico_Database -f views_postgresql.sql

-- ============================================================
-- View: vw_Areas
-- Descrição: Lista áreas com nome da empresa
-- ============================================================
CREATE OR REPLACE VIEW vw_Areas AS
SELECT
    a.ID,
    a.AREA_NOME,
    a.ID_EMPRESA,
    e.EMPRESA_NOME
FROM Areas a
JOIN Empresas e ON e.ID = a.ID_EMPRESA;

-- Comment na view
COMMENT ON VIEW vw_Areas IS 'View de áreas com informações da empresa';


-- ============================================================
-- View: vw_Equipes
-- Descrição: Lista equipes com área e empresa
-- ============================================================
CREATE OR REPLACE VIEW vw_Equipes AS
SELECT
    eq.ID_EQUIPE,
    eq.NOME_EQUIPE,
    eq.ID_AREA,
    a.AREA_NOME,
    a.ID_EMPRESA,
    e.EMPRESA_NOME,
    eq.GERENTE
FROM Equipes eq
JOIN Areas a ON a.ID = eq.ID_AREA
JOIN Empresas e ON e.ID = a.ID_EMPRESA;

-- Comment na view
COMMENT ON VIEW vw_Equipes IS 'View de equipes com informações de área e empresa';


-- ============================================================
-- View: vw_RH_Colaborador_Atual
-- Descrição: Lista colaboradores ativos com todos os dados relacionados
-- ============================================================
CREATE OR REPLACE VIEW vw_RH_Colaborador_Atual AS
SELECT
    p.ID_PESSOA,
    p.CPF,
    p.NOME,
    p.SEXO,
    p.NASCIMENTO,
    p.EMAIL_CORPORATIVO,
    p.EMAIL_PESSOAL,
    p.TEL_PESSOAL,
    p.TEL_CORPORATIVO,
    c.ID_CONTRATACAO,
    c.INICIO,
    c.STATUS,
    e.EMPRESA_NOME,
    a.AREA_NOME,
    eq.NOME_EQUIPE,
    cg.CARGO_NOME,
    nv.NIVEL_NOME,
    ct.CONTRATO_NOME
FROM RH_Contratacoes c
JOIN RH_Pessoas p ON p.ID_PESSOA = c.ID_PESSOA
JOIN Empresas e ON e.ID = c.ID_EMPRESA
JOIN Areas a ON a.ID = c.ID_AREA
LEFT JOIN Equipes eq ON eq.ID_EQUIPE = c.ID_EQUIPE
JOIN RH_Cargos cg ON cg.ID_CARGO = c.ID_CARGO
LEFT JOIN RH_Niveis nv ON nv.ID_NIVEL = c.ID_NIVEL
JOIN RH_Contratos ct ON ct.ID_CONTRATO = c.ID_CONTRATO
WHERE c.SAIDA IS NULL;

-- Comment na view
COMMENT ON VIEW vw_RH_Colaborador_Atual IS 'View de colaboradores ativos com dados completos de contratação';


-- ============================================================
-- Testes das Views
-- ============================================================

-- Teste vw_Areas
-- SELECT * FROM vw_Areas LIMIT 10;

-- Teste vw_Equipes
-- SELECT * FROM vw_Equipes LIMIT 10;

-- Teste vw_RH_Colaborador_Atual
-- SELECT * FROM vw_RH_Colaborador_Atual LIMIT 10;


-- ============================================================
-- Verificar se as views foram criadas corretamente
-- ============================================================

-- Listar todas as views
-- SELECT tablename FROM pg_views WHERE schemaname = 'public' ORDER BY tablename;

-- Verificar estrutura das views
-- \d vw_Areas
-- \d vw_Equipes
-- \d vw_RH_Colaborador_Atual
