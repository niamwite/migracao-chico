# Plano de Migração: MySQL → PostgreSQL


## Banco de Dados: `Unico_Database`

**Tabelas:** 27

### ⚠️ Avisos (23)
- ⚠️ Areas: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Empresas: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_Meta_Campanhas: Coluna 'id_pk': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_Meta_Costs: Coluna 'id_pk': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_DealsInProgress: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_DealsLost: Coluna 'id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_DealsWin: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_EtapasFunil: Coluna 'id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_Funis: Coluna 'id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_Teams: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Marketing_RD_Users: Coluna 'id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Meta_Forms: Coluna 'meta_forms_id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ Meta_Leads: Coluna 'ID': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Cargo_Regras: Coluna 'ID_REGRA': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Cargos: Coluna 'ID_CARGO': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Colaboradores: Coluna 'ID_COLABORADOR': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Contratacoes: Coluna 'ID_CONTRATACAO': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Contratacoes_Motivos: Coluna 'ID_MOTIVO': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Contratos: Coluna 'ID_CONTRATO': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Niveis: Coluna 'ID_NIVEL': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ RH_Pessoas: Coluna 'ID_PESSOA': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ stg_RH_Cargo_Regras: Coluna 'stg_id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL
- ⚠️ stg_RH_Colaboradores: Coluna 'stg_id': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL

### Estrutura das Tabelas

#### `Areas`

**Colunas:**
  - `ID`: int(10) unsigned → `integer` [NULL: ✗]
  - `AREA_NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `ID_EMPRESA`: int(10) unsigned → `integer` [NULL: ✗]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `uq_areas_empresa_area` (`ID_EMPRESA`, `AREA_NOME`)
  - UNIQUE `uq_areas_id_area_nome` (`ID`, `AREA_NOME`)
  - `idx_areas_id_empresa` (`ID_EMPRESA`)

#### `Empresas`

**Colunas:**
  - `ID`: int(10) unsigned → `integer` [NULL: ✗]
  - `EMPRESA_NOME`: varchar(100) → `varchar(100)` [NULL: ✗]
  - `RAZAO_SOCIAL`: varchar(200) → `varchar(200)` [NULL: ✓]
  - `CNPJ`: char(14) → `char(14)` [NULL: ✓]
  - `CPF_PROPRIETARIO`: char(11) → `char(11)` [NULL: ✓]
  - `NOME_PROPRIETARIO`: varchar(150) → `varchar(150)` [NULL: ✓]
  - `ENDERECO`: varchar(250) → `varchar(250)` [NULL: ✓]
  - `CEP`: char(8) → `char(8)` [NULL: ✓]
  - `CIDADE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `ESTADO`: char(2) → `char(2)` [NULL: ✓]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `uq_empresas_empresa_nome` (`EMPRESA_NOME`)
  - UNIQUE `uq_empresas_id_nome` (`ID`, `EMPRESA_NOME`)
  - UNIQUE `uk_empresas_nome` (`EMPRESA_NOME`)
  - UNIQUE `uk_empresas_cnpj` (`CNPJ`)

#### `Equipes`

**Colunas:**
  - `ID_EQUIPE`: int(10) unsigned → `integer` [NULL: ✗]
  - `NOME_EQUIPE`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `ID_AREA`: int(10) unsigned → `integer` [NULL: ✗]
  - `GERENTE`: varchar(150) → `varchar(150)` [NULL: ✓]

**Primary Key:** `ID_EQUIPE`

**Índices:**
  - UNIQUE `uq_equipes_nome_area` (`NOME_EQUIPE`, `ID_AREA`)
  - `idx_equipes_id_area` (`ID_AREA`)

#### `Marketing_Meta_Campanhas`

**Colunas:**
  - `id_pk`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `ad_account_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `campaign_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `status`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `effective_status`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `objective`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `created_time`: datetime → `date` [NULL: ✓]
  - `updated_time`: datetime → `date` [NULL: ✓]
  - `start_time`: datetime → `date` [NULL: ✓]
  - `stop_time`: datetime → `date` [NULL: ✓]
  - `ingested_at`: datetime → `date` [NULL: ✗]

**Primary Key:** `id_pk`

**Índices:**
  - UNIQUE `uk_adaccount_campaign` (`campaign_id`)
  - `idx_effective_status` (`effective_status`)
  - `idx_updated_time` (`updated_time`)
  - `ad_account_id` (`ad_account_id`)

#### `Marketing_Meta_Costs`

**Colunas:**
  - `id_pk`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `unique_key`: varchar(80) → `varchar(80)` [NULL: ✗]
  - `date_start`: date → `date` [NULL: ✗]
  - `date_stop`: date → `date` [NULL: ✓]
  - `account_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `account_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `campaign_id`: varchar(32) → `varchar(32)` [NULL: ✓]
  - `campaign_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `ad_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `ad_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `impressions`: bigint(20) unsigned → `bigint` [NULL: ✓]
  - `spend`: decimal(18,6) → `numeric(18,6)` [NULL: ✓]
  - `extracted_at`: datetime → `date` [NULL: ✗]
  - `updated_at`: datetime → `date` [NULL: ✗]

**Primary Key:** `id_pk`

**Índices:**
  - UNIQUE `uq_unique_key` (`unique_key`)
  - `idx_date_start` (`date_start`)
  - `idx_ad_id` (`ad_id`)
  - `idx_campaign_id` (`campaign_id`)
  - `idx_account_id` (`account_id`)

#### `Marketing_RD_DealsInProgress`

**Colunas:**
  - `ID`: bigint(20) → `bigint` [NULL: ✗]
  - `deal_id`: varchar(100) → `varchar(100)` [NULL: ✗]
  - `deal_stage_key`: varchar(400) → `varchar(400)` [NULL: ✗]
  - `name`: varchar(300) → `varchar(300)` [NULL: ✗]
  - `contact_email`: varchar(190) → `varchar(190)` [NULL: ✓]
  - `contact_phone`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `amount_total`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `amount_unique`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `amount_monthly`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `prediction_date`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `created_at`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `updated_at`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `win`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `closed_at`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `interactions`: varchar(100) → `varchar(100)` [NULL: ✓]
  - `rating`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `user_id`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `user_name`: varchar(150) → `varchar(150)` [NULL: ✗]
  - `stage_id`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `stage_name`: varchar(100) → `varchar(100)` [NULL: ✗]
  - `source_id`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `campaign_id`: varchar(100) → `varchar(100)` [NULL: ✓]
  - `is_paused`: tinyint(1) → `smallint` [NULL: ✗]
  - `status_ongoing`: varchar(20) → `varchar(20)` [NULL: ✗]
  - `hold_raw`: longtext → `text` [NULL: ✓]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `uq_deal_stage_key` (`deal_stage_key`)
  - `idx_deal_id` (`deal_id`)
  - `idx_stage_id` (`stage_id`)
  - `idx_updated_at` (`updated_at`)
  - `idx_campaign_id` (`campaign_id`)
  - `idx_contact_email` (`contact_email`)

#### `Marketing_RD_DealsLost`

**Colunas:**
  - `id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `loss_event_id`: char(150) → `char(150)` [NULL: ✗]
  - `deal_id`: char(24) → `char(24)` [NULL: ✗]
  - `stage_id`: char(24) → `char(24)` [NULL: ✓]
  - `stage_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `user_id`: char(24) → `char(24)` [NULL: ✓]
  - `user_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `amount_total`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `amount_unique`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `amount_monthly`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `created_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `updated_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `closed_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `win`: tinyint(1) → `smallint` [NULL: ✓]
  - `source_id`: varchar(64) → `varchar(64)` [NULL: ✓]
  - `user_changed`: tinyint(1) → `smallint` [NULL: ✓]
  - `lost_reason_id`: varchar(64) → `varchar(64)` [NULL: ✓]
  - `lost_reason_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `contacts_json`: longtext → `text` [NULL: ✓]
  - `payload_json`: longtext → `text` [NULL: ✓]
  - `event_key`: char(64) → `char(64)` [NULL: ✗]
  - `ingested_at`: timestamp → `timestamp` [NULL: ✗]
  - `updated_ingest`: timestamp → `timestamp` [NULL: ✗]

**Primary Key:** `id`

**Índices:**
  - UNIQUE `uq_dealslost_event_key` (`event_key`)
  - UNIQUE `uq_dealslost_loss_event_id` (`loss_event_id`)
  - `idx_dealslost_deal_id` (`deal_id`)
  - `idx_dealslost_stage_id` (`stage_id`)
  - `idx_dealslost_user_id` (`user_id`)
  - `idx_dealslost_win` (`win`)

#### `Marketing_RD_DealsWin`

**Colunas:**
  - `ID`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `deal_id`: char(24) → `char(24)` [NULL: ✗]
  - `name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `amount_total`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `amount_unique`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `amount_monthly`: decimal(18,2) → `numeric(18,2)` [NULL: ✓]
  - `created_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `updated_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `closed_at`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `win`: tinyint(1) → `smallint` [NULL: ✓]
  - `user_id`: char(24) → `char(24)` [NULL: ✓]
  - `user_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `source_id`: varchar(64) → `varchar(64)` [NULL: ✓]
  - `user_changed`: tinyint(1) → `smallint` [NULL: ✓]
  - `contacts_json`: longtext → `text` [NULL: ✓]
  - `ingested_at`: timestamp → `timestamp` [NULL: ✗]
  - `updated_ingest`: timestamp → `timestamp` [NULL: ✗]
  - `stage_id`: char(24) → `char(24)` [NULL: ✓]
  - `stage_name`: varchar(255) → `varchar(255)` [NULL: ✓]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `uq_dealswin_deal_id` (`deal_id`)
  - `idx_dealswin_user_id` (`user_id`)
  - `idx_dealswin_win` (`win`)
  - `idx_dealswin_stage_id` (`stage_id`)

#### `Marketing_RD_EtapasFunil`

**Colunas:**
  - `id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `stage_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `stage_name`: varchar(255) → `varchar(255)` [NULL: ✗]
  - `stage_order`: int(11) → `integer` [NULL: ✓]
  - `rd_pipeline_id`: varchar(32) → `varchar(32)` [NULL: ✓]
  - `rd_pipeline_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `payload`: longtext → `text` [NULL: ✓]
  - `loaded_at`: timestamp → `timestamp` [NULL: ✗]

**Primary Key:** `id`

**Índices:**
  - UNIQUE `uk_rd_stage_id` (`stage_id`)
  - `idx_pipeline` (`rd_pipeline_id`)

#### `Marketing_RD_Funis`

**Colunas:**
  - `id`: int(10) unsigned → `integer` [NULL: ✗]
  - `pipeline_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `pipeline_name`: varchar(255) → `varchar(255)` [NULL: ✗]
  - `pipeline_order`: int(11) → `integer` [NULL: ✓]
  - `deal_stages_count`: int(11) → `integer` [NULL: ✓]
  - `config_json`: longtext → `text` [NULL: ✓]
  - `deal_stages_json`: longtext → `text` [NULL: ✓]
  - `synced_at`: datetime → `date` [NULL: ✗]

**Primary Key:** `id`

**Índices:**
  - UNIQUE `uq_pipeline_id` (`pipeline_id`)
  - `idx_pipeline_order` (`pipeline_order`)
  - `idx_pipeline_name` (`pipeline_name`)

#### `Marketing_RD_Teams`

**Colunas:**
  - `ID`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `rd_team_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `team_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `is_active`: tinyint(1) → `smallint` [NULL: ✓]
  - `created_at`: datetime → `date` [NULL: ✓]
  - `updated_at`: datetime → `date` [NULL: ✓]
  - `raw_json`: longtext → `text` [NULL: ✓]
  - `ingested_at`: timestamp → `timestamp` [NULL: ✗]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `uq_dim_teams_rd_team_id` (`rd_team_id`)
  - `idx_team_name` (`team_name`)

#### `Marketing_RD_Users`

**Colunas:**
  - `id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `rd_user_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `user_name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `email`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `active`: tinyint(1) → `smallint` [NULL: ✗]
  - `hidden`: tinyint(1) → `smallint` [NULL: ✗]
  - `created_at`: datetime → `date` [NULL: ✓]
  - `updated_at`: datetime → `date` [NULL: ✓]
  - `last_login`: datetime → `date` [NULL: ✓]
  - `payload`: longtext → `text` [NULL: ✓]
  - `loaded_at`: timestamp → `timestamp` [NULL: ✗]

**Primary Key:** `id`

**Índices:**
  - UNIQUE `uk_rd_user_id` (`rd_user_id`)
  - `idx_email` (`email`)
  - `idx_active` (`active`)

#### `Meta_Forms`

**Colunas:**
  - `meta_forms_id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `form_id`: varchar(32) → `varchar(32)` [NULL: ✗]
  - `locale`: varchar(10) → `varchar(10)` [NULL: ✓]
  - `name`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `status`: varchar(20) → `varchar(20)` [NULL: ✓]

**Primary Key:** `meta_forms_id`

**Índices:**
  - UNIQUE `uk_meta_forms__form_id` (`form_id`)

#### `Meta_Leads`

**Colunas:**
  - `ID`: int(11) → `integer` [NULL: ✗]
  - `lead_id`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `form_id`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `created_time`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `ad_id`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `ad_name`: varchar(159) → `varchar(159)` [NULL: ✓]
  - `campaign_id`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `campaign_name`: varchar(59) → `varchar(59)` [NULL: ✓]
  - `is_organic`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `post`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `qual_o_valor_do_credito_desejado`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `qual_seu_faturamento_mensal_comprovado`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `full_name`: varchar(85) → `varchar(85)` [NULL: ✗]
  - `para_qual_finalidade`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `qual_e_a_sua_urgencia_para_adquirir_o_recurso`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `company_name`: varchar(297) → `varchar(297)` [NULL: ✓]
  - `phone_number`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `voce_possui_algum_tipo_de_garantia`: varchar(50) → `varchar(50)` [NULL: ✗]
  - `job_title`: varchar(365) → `varchar(365)` [NULL: ✓]
  - `email`: varchar(116) → `varchar(116)` [NULL: ✗]
  - `utm_source`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `utm_medium`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `utm_campaign`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `utm_content`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `utm_term`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `voce_esta_ciente_de_que_nossos_servicos_sao_destinados_a_empresa`: varchar(50) → `varchar(50)` [NULL: ✓]

**Primary Key:** `ID`

**Índices:**
  - UNIQUE `lead_id` (`lead_id`)

#### `RH_Cargo_Regras`

**Colunas:**
  - `ID_REGRA`: int(10) unsigned → `integer` [NULL: ✗]
  - `ID_CARGO`: smallint(5) unsigned → `smallint` [NULL: ✗]
  - `ID_AREA`: int(10) unsigned → `integer` [NULL: ✗]
  - `ID_EQUIPE`: int(10) unsigned → `integer` [NULL: ✓]

**Primary Key:** `ID_REGRA`

**Índices:**
  - UNIQUE `uk_regra` (`ID_CARGO`, `ID_AREA`, `ID_EQUIPE`)
  - `idx_regra_area` (`ID_AREA`, `ID_EQUIPE`)
  - `fk_regra_equipe` (`ID_EQUIPE`)

#### `RH_Cargos`

**Colunas:**
  - `ID_CARGO`: smallint(5) unsigned → `smallint` [NULL: ✗]
  - `CARGO_NOME`: varchar(80) → `varchar(80)` [NULL: ✗]

**Primary Key:** `ID_CARGO`

**Índices:**
  - UNIQUE `uk_cargo_nome` (`CARGO_NOME`)

#### `RH_Colaboradores`

**Colunas:**
  - `ID_COLABORADOR`: int(10) unsigned → `integer` [NULL: ✗]
  - `RH_ID`: int(10) unsigned → `integer` [NULL: ✓]
  - `NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `STATUS`: varchar(20) → `varchar(20)` [NULL: ✗]
  - `CONTRATO`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `INICIO`: date → `date` [NULL: ✗]
  - `SAIDA`: date → `date` [NULL: ✓]
  - `MOTIVO`: varchar(200) → `varchar(200)` [NULL: ✓]
  - `SEXO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NASCIMENTO`: date → `date` [NULL: ✓]
  - `CPF`: char(11) → `char(11)` [NULL: ✓]
  - `RG`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `ID_EMPRESA`: int(10) unsigned → `integer` [NULL: ✗]
  - `ID_AREA`: int(10) unsigned → `integer` [NULL: ✓]
  - `ID_EQUIPE`: int(10) unsigned → `integer` [NULL: ✓]
  - `CARGO`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `TEL_PESSOAL`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CONTATO_EMERGENCIA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `TEL_CORPORATIVO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NOME_MAE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `ENDERECO`: varchar(200) → `varchar(200)` [NULL: ✓]
  - `CIDADE`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `ESTADO`: char(2) → `char(2)` [NULL: ✓]
  - `EMAIL_CORPORATIVO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `EMAIL_PESSOAL`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `BANCO`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `AGENCIA`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CONTA_CORR`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CONTA_POUP`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `TIPO_PIX`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CHAVE_PIX`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `FOTO`: varchar(512) → `varchar(512)` [NULL: ✓]
  - `created_at`: datetime → `date` [NULL: ✗]
  - `updated_at`: datetime → `date` [NULL: ✗]

**Primary Key:** `ID_COLABORADOR`

**Índices:**
  - UNIQUE `uk_rh_colab_rh_id` (`RH_ID`)
  - UNIQUE `uk_rh_colab_cpf` (`CPF`)
  - UNIQUE `uk_rh_colab_emailcorp` (`EMAIL_CORPORATIVO`)
  - `idx_rh_colab_empresa` (`ID_EMPRESA`)
  - `idx_rh_colab_area` (`ID_AREA`)
  - `idx_rh_colab_equipe` (`ID_EQUIPE`)

#### `RH_Contratacoes`

**Colunas:**
  - `ID_CONTRATACAO`: int(10) unsigned → `integer` [NULL: ✗]
  - `RH_ID`: int(10) unsigned → `integer` [NULL: ✓]
  - `ID_PESSOA`: int(10) unsigned → `integer` [NULL: ✗]
  - `ID_PESSOA_ATUAL`: int(10) unsigned → `integer` [NULL: ✓]
  - `STATUS`: varchar(20) → `varchar(20)` [NULL: ✗]
  - `ID_CONTRATO`: tinyint(3) unsigned → `smallint` [NULL: ✗]
  - `INICIO`: date → `date` [NULL: ✗]
  - `SAIDA`: date → `date` [NULL: ✓]
  - `ID_MOTIVO`: int(10) unsigned → `integer` [NULL: ✓]
  - `ID_EMPRESA`: int(10) unsigned → `integer` [NULL: ✗]
  - `ID_AREA`: int(10) unsigned → `integer` [NULL: ✓]
  - `ID_EQUIPE`: int(10) unsigned → `integer` [NULL: ✓]
  - `ID_CARGO`: smallint(5) unsigned → `smallint` [NULL: ✓]
  - `ID_NIVEL`: tinyint(3) unsigned → `smallint` [NULL: ✓]
  - `created_at`: datetime → `date` [NULL: ✗]
  - `updated_at`: datetime → `date` [NULL: ✗]
  - `deleted_at`: datetime → `date` [NULL: ✓]

**Primary Key:** `ID_CONTRATACAO`

**Índices:**
  - UNIQUE `uk_rh_id` (`RH_ID`)
  - UNIQUE `uk_pessoa_atual` (`ID_PESSOA_ATUAL`)
  - `idx_vinc_pessoa` (`ID_PESSOA`)
  - `idx_vinc_empresa` (`ID_EMPRESA`)
  - `idx_vinc_area` (`ID_AREA`)
  - `idx_vinc_equipe` (`ID_EQUIPE`)
  - `idx_vinc_cargo` (`ID_CARGO`)
  - `fk_vinc_contrato` (`ID_CONTRATO`)
  - `fk_vinc_nivel` (`ID_NIVEL`)
  - `idx_contr_pessoa_inicio` (`ID_PESSOA`, `INICIO`)
  - `idx_contr_ativo` (`ID_PESSOA_ATUAL`)
  - `idx_contr_empresa` (`ID_EMPRESA`)
  - `idx_contr_area` (`ID_AREA`)
  - `idx_contr_equipe` (`ID_EQUIPE`)
  - `idx_contr_cargo` (`ID_CARGO`)
  - `idx_contr_id_motivo` (`ID_MOTIVO`)

#### `RH_Contratacoes_Motivos`

**Colunas:**
  - `ID_MOTIVO`: int(10) unsigned → `integer` [NULL: ✗]
  - `MOTIVO_NOME`: varchar(100) → `varchar(100)` [NULL: ✗]

**Primary Key:** `ID_MOTIVO`

**Índices:**
  - UNIQUE `uk_motivo_nome` (`MOTIVO_NOME`)

#### `RH_Contratos`

**Colunas:**
  - `ID_CONTRATO`: tinyint(3) unsigned → `smallint` [NULL: ✗]
  - `CONTRATO_NOME`: varchar(30) → `varchar(30)` [NULL: ✗]

**Primary Key:** `ID_CONTRATO`

**Índices:**
  - UNIQUE `uk_contrato_nome` (`CONTRATO_NOME`)

#### `RH_Niveis`

**Colunas:**
  - `ID_NIVEL`: tinyint(3) unsigned → `smallint` [NULL: ✗]
  - `NIVEL_NOME`: varchar(20) → `varchar(20)` [NULL: ✗]

**Primary Key:** `ID_NIVEL`

**Índices:**
  - UNIQUE `uk_nivel_nome` (`NIVEL_NOME`)

#### `RH_Pessoas`

**Colunas:**
  - `ID_PESSOA`: int(10) unsigned → `integer` [NULL: ✗]
  - `NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `SEXO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NASCIMENTO`: date → `date` [NULL: ✓]
  - `CPF`: char(11) → `char(11)` [NULL: ✓]
  - `RG`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NOME_MAE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `TEL_PESSOAL`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `TEL_CORPORATIVO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CONTATO_EMERGENCIA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `EMAIL_CORPORATIVO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `EMAIL_PESSOAL`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `ENDERECO`: varchar(200) → `varchar(200)` [NULL: ✓]
  - `CIDADE`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `ESTADO`: char(2) → `char(2)` [NULL: ✓]
  - `BANCO`: varchar(80) → `varchar(80)` [NULL: ✓]
  - `AGENCIA`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CONTA_CORR`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CONTA_POUP`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `TIPO_PIX`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CHAVE_PIX`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `FOTO`: varchar(512) → `varchar(512)` [NULL: ✓]
  - `created_at`: datetime → `date` [NULL: ✗]
  - `updated_at`: datetime → `date` [NULL: ✗]
  - `deleted_at`: datetime → `date` [NULL: ✓]

**Primary Key:** `ID_PESSOA`

**Índices:**
  - UNIQUE `uk_pessoa_cpf` (`CPF`)
  - `idx_pessoa_emailcorp` (`EMAIL_CORPORATIVO`)
  - `idx_pessoa_nome` (`NOME`)
  - `idx_pessoas_cpf` (`CPF`)
  - `idx_pessoas_nome` (`NOME`)

#### `stg_RH_Cargo_Regras`

**Colunas:**
  - `stg_id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `imported_at`: datetime → `date` [NULL: ✗]
  - `EMPRESA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `AREA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `EQUIPE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `CARGO`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `NIVEL`: varchar(30) → `varchar(30)` [NULL: ✓]

**Primary Key:** `stg_id`

**Índices:**
  - `idx_stg_empresa_area` (`EMPRESA`, `AREA`)
  - `idx_stg_equipe` (`EQUIPE`)
  - `idx_stg_cargo` (`CARGO`)
  - `idx_stg_nivel` (`NIVEL`)

#### `stg_RH_Colaboradores`

**Colunas:**
  - `stg_id`: bigint(20) unsigned → `bigint` [NULL: ✗]
  - `imported_at`: datetime → `date` [NULL: ✗]
  - `source_system`: varchar(50) → `varchar(50)` [NULL: ✓]
  - `source_sheet`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `source_row_number`: int(10) unsigned → `integer` [NULL: ✓]
  - `row_hash`: char(64) → `char(64)` [NULL: ✓]
  - `is_processed`: tinyint(1) → `smallint` [NULL: ✗]
  - `processed_at`: datetime → `date` [NULL: ✓]
  - `notes`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `ID`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NOME`: varchar(160) → `varchar(160)` [NULL: ✓]
  - `STATUS`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CONTRATO`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `INICIO`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `SAIDA`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `MOTIVO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `SEXO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NASCIMENTO`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CPF`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `RG`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `EMPRESA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `EQUIPE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `AREA`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `CARGO`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `NIVEL`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `TEL_PESSOAL`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CONTATO_EMERGENCIA`: varchar(160) → `varchar(160)` [NULL: ✓]
  - `TEL_CORPORATIVO`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `NOME_MAE`: varchar(160) → `varchar(160)` [NULL: ✓]
  - `ENDERECO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `CIDADE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `ESTADO`: varchar(10) → `varchar(10)` [NULL: ✓]
  - `EMAIL_CORPORATIVO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `EMAIL_PESSOAL`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `BANCO`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `AGENCIA`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CONTA_CORR`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `CONTA_POUP`: varchar(40) → `varchar(40)` [NULL: ✓]
  - `TIPO_PIX`: varchar(30) → `varchar(30)` [NULL: ✓]
  - `CHAVE_PIX`: varchar(160) → `varchar(160)` [NULL: ✓]
  - `FOTO`: varchar(512) → `varchar(512)` [NULL: ✓]

**Primary Key:** `stg_id`

**Índices:**
  - `idx_stg_imported_at` (`imported_at`)
  - `idx_stg_id` (`ID`)
  - `idx_stg_cpf` (`CPF`)
  - `idx_stg_emailcorp` (`EMAIL_CORPORATIVO`)
  - `idx_stg_row_hash` (`row_hash`)
  - `idx_stg_processed` (`is_processed`, `imported_at`)

#### `vw_Areas`

**Colunas:**
  - `ID`: int(10) unsigned → `integer` [NULL: ✗]
  - `AREA_NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `ID_EMPRESA`: int(10) unsigned → `integer` [NULL: ✗]
  - `EMPRESA_NOME`: varchar(100) → `varchar(100)` [NULL: ✗]

#### `vw_Equipes`

**Colunas:**
  - `ID_EQUIPE`: int(10) unsigned → `integer` [NULL: ✗]
  - `NOME_EQUIPE`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `ID_AREA`: int(10) unsigned → `integer` [NULL: ✗]
  - `AREA_NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `ID_EMPRESA`: int(10) unsigned → `integer` [NULL: ✗]
  - `EMPRESA_NOME`: varchar(100) → `varchar(100)` [NULL: ✗]
  - `GERENTE`: varchar(150) → `varchar(150)` [NULL: ✓]

#### `vw_RH_Colaborador_Atual`

**Colunas:**
  - `ID_PESSOA`: int(10) unsigned → `integer` [NULL: ✗]
  - `CPF`: char(11) → `char(11)` [NULL: ✓]
  - `NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `SEXO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `NASCIMENTO`: date → `date` [NULL: ✓]
  - `EMAIL_CORPORATIVO`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `EMAIL_PESSOAL`: varchar(255) → `varchar(255)` [NULL: ✓]
  - `TEL_PESSOAL`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `TEL_CORPORATIVO`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `ID_CONTRATACAO`: int(10) unsigned → `integer` [NULL: ✗]
  - `INICIO`: date → `date` [NULL: ✗]
  - `STATUS`: varchar(20) → `varchar(20)` [NULL: ✗]
  - `EMPRESA_NOME`: varchar(100) → `varchar(100)` [NULL: ✗]
  - `AREA_NOME`: varchar(120) → `varchar(120)` [NULL: ✗]
  - `NOME_EQUIPE`: varchar(120) → `varchar(120)` [NULL: ✓]
  - `CARGO_NOME`: varchar(80) → `varchar(80)` [NULL: ✗]
  - `NIVEL_NOME`: varchar(20) → `varchar(20)` [NULL: ✓]
  - `CONTRATO_NOME`: varchar(30) → `varchar(30)` [NULL: ✗]


## 📋 Resumo e Recomendações

**Estatísticas:**
- Bancos de dados: 1
- Total de tabelas: 27
- Problemas críticos: 0
- Avisos: 23

✅ **Nenhum problema crítico encontrado!**

⚠️ **23 aviso(s) encontrado(s)**

### 🛠️ Estratégia de Migração Recomendada:

1. **Backup completo do MySQL**
   ```bash
   mysqldump -h 46.62.152.123 -u willkoga -p --single-transaction --routines --triggers --all-databases > backup_mysql.sql
   ```

2. **Instalar PostgreSQL** e criar bancos correspondentes

3. **Usar ferramenta de migração**:
   - **pgloader** (recomendado - automático)
   - **mysql2pgsql**
   - Script customizado

4. **Exemplo com pgloader:**
   ```bash
   pgloader mysql://willkoga:Sucesso2026@46.62.152.123/nome_db postgresql://user@localhost/nome_db
   ```

5. **Migrar esquema** (CREATE TABLE, indexes, constraints)

6. **Migrar dados** (INSERT/COPY)

7. **Recriar views, stored procedures, triggers**

8. **Validar dados** e **testar aplicação**

9. **Performance tuning** (ANALYZE, VACUUM, índices)

### 📦 Instalação das Ferramentas:

```bash
# Cliente PostgreSQL
sudo pacman -S postgresql postgresql-clients

# pgloader (ferramenta de migração)
sudo pacman -S pgloader

# OU mysql2pgsql (Python)
pip install mysql2pgsql
```