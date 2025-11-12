# 🚀 Projeto Secretaria SkyPen (Full Stack)
Um sistema completo de gerenciamento de secretaria escolar, projetado para ser intuitivo e eficiente. O sistema integra um backend robusto em Django com um frontend moderno e reativo construído com React + Vite.


## Configuração Obrigatória

### -Cadastro de Bimestres

Para que o módulo de Criação de Notas funcione corretamente, é essencial que os Bimestres sejam cadastrados previamente através do painel de administração do Django (/admin).

Importante: Os bimestres devem ser criados na ordem cronológica correta (ex: 1º Bimestre, 2º Bimestre, 3º Bimestre, 4º Bimestre), pois a lógica de lançamento de notas depende dessa sequência.

Acesse o painel **/admin**.

Encontre o modelo referente aos "Bimestres".

**Crie os registros na ordem exata (1º, 2º, etc.)**.
