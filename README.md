# Projeto secretaria SkyPen , integrado com funcionalidades do back e no front completas


## Configuração Obrigatória

### -Cadastro de Bimestres

Para que o módulo de Criação de Notas funcione corretamente, é essencial que os Bimestres sejam cadastrados previamente através do painel de administração do Django (/admin).

Importante: Os bimestres devem ser criados na ordem cronológica correta (ex: 1º Bimestre, 2º Bimestre, 3º Bimestre, 4º Bimestre), pois a lógica de lançamento de notas depende dessa sequência.

Acesse o painel **/admin**.

Encontre o modelo referente aos "Bimestres".

**Crie os registros na ordem exata (1º, 2º, etc.)**.
