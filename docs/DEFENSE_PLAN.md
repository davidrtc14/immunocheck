# Plano de defesa e apresentação

Versão-base para uma apresentação de 12 a 15 minutos. Ajustar ao tempo formal da
banca. Todas as demonstrações usam fixtures sintéticas; somente o autor interage com
o bot.

## Mensagem central

O ImmunoCheck não tenta substituir especialistas nem declarar a verdade universal.
Ele demonstra que uma pipeline local de LLM e RAG pode comparar alegações sobre
vacinação com um corpus delimitado, abster-se e mostrar fontes rastreáveis em um
computador doméstico, com desempenho e limitações medidos.

## Estrutura sugerida

| Slide | Conteúdo | Tempo |
|---|---|---:|
| 1 | Título, autor, orientador e problema | 0:40 |
| 2 | Motivação e pergunta de pesquisa | 1:00 |
| 3 | Requisitos e escopo | 1:00 |
| 4 | Arquitetura v3 | 1:40 |
| 5 | Corpus e método experimental | 1:30 |
| 6 | Evolução v1 → v2 → v3 | 1:20 |
| 7 | Resultados quantitativos | 1:40 |
| 8 | Demonstração ou gravação curta | 2:30 |
| 9 | LGPD, ética e limitações | 1:30 |
| 10 | Conclusão e contribuições | 0:50 |

## Conteúdo e fala por slide

### 1. Título

**Na tela:** título curto, autor, curso, orientador e uma frase: “veredito com fontes,
execução local e possibilidade de abstenção”.

**Fala:** “Este trabalho apresenta o ImmunoCheck, um protótipo acadêmico para
verificação documental de alegações sobre vacinação humana. O foco não é substituir
uma avaliação clínica, mas produzir uma análise rastreável em hardware doméstico.”

### 2. Motivação e pergunta

**Na tela:** circulação rápida de informação; risco de respostas não fundamentadas;
pergunta de pesquisa.

**Fala:** “A dificuldade não está apenas em chamar uma LLM. Em saúde, precisamos
distinguir falsidade, distorção e falta de evidência, além de mostrar de onde veio a
resposta. A pergunta foi se isso seria viável localmente e com fontes verificáveis.”

### 3. Requisitos e escopo

**Na tela:** texto, imagem e link; quatro classes; Telegram; gratuito/local; sem
memória. Coluna separada: vídeo, WhatsApp, diagnóstico e implantação pública fora.

**Fala:** “O escopo foi deliberadamente limitado. Vídeo seria uma subpesquisa de
transcrição e seleção de quadros. WhatsApp adicionaria custo e burocracia. Não há
cache conversacional nem armazenamento de mensagens.”

### 4. Arquitetura v3

```text
entrada → normalização → alegação → BGE-M3 top 15 → roteador
                    ├─ simples → decisor top 6
                    ├─ premissa-conclusão → decisor top 15
                    └─ evento sem âncora → evidência insuficiente
                 → citações hierárquicas → resposta
```

**Fala:** “A LLM não cria links. Ela escolhe identificadores dos trechos fornecidos,
e a aplicação monta título, URL, data e página usando os metadados do corpus. IDs
inválidos falham de modo fechado.”

### 5. Corpus e método

**Na tela:** 80 documentos, 7.585 chunks, fontes oficiais/científicas; 160 itens na
linha histórica; 32 itens e oito famílias novas na confirmação v3; conjuntos
separados.

**Fala:** “A avaliação não usa as mensagens do Telegram. As alegações são sintéticas
e documentais. Famílias são separadas para reduzir vazamento por paráfrase. O teste
histórico foi executado uma vez e não serviu para ajustar a v3.”

### 6. Evolução da solução

**Na tela:**

- v1: integração completa, auditor conservador, recall zero de `MISLEADING`;
- v2: hipóteses separadas, nenhuma passou os gates, linha encerrada;
- v3: roteamento + decisão especializada + citações hierárquicas.

**Fala:** “Preservamos também os resultados negativos. O reranker melhorou o ranking,
mas não o sistema completo; o auditor aumentou abstenções e eliminou respostas
úteis. A arquitetura final nasceu desses testes, não de preferência tecnológica.”

### 7. Resultados

**Na tela:** tabela curta.

| Métrica na confirmação nova | v1 | v3 |
|---|---:|---:|
| Macro-F1 | 0,482 | 0,846 |
| Acurácia | 0,531 | 0,844 |
| Recall `MISLEADING` | 0,000 | 0,625 |
| Precisão de abstenção | 0,333 | 1,000 |
| Citação exata | 0,667 | 0,833 |
| P95 | 12,09 s | 19,35 s |

**Fala:** “A melhora teve custo de latência, mas permaneceu abaixo do gate de vinte
segundos. São 32 itens sintéticos; portanto, estes números não representam a internet
real nem permitem alegar precisão clínica.”

Em nota separada, informar que a v1 teve macro-F1 0,416 no teste histórico de 64
itens. Não colocar 0,416 e 0,846 na mesma coluna de comparação direta, porque são
amostras diferentes.

### 8. Demonstração

Roteiro principal:

1. mostrar `/privacidade`;
2. enviar `A vacina tríplice viral causa autismo.`;
3. apontar veredito, explicação, fato correto e fontes;
4. abrir uma fonte já preparada;
5. se houver tempo, mostrar a imagem sintética;
6. encerrar o bot ao final.

Plano B: executar a mesma alegação pela CLI. Se a rede falhar, não improvisar outra
entrada e não tentar corrigir o sistema ao vivo.

### 9. LGPD, ética e limitações

**Na tela:** processamento local; sem persistência; Telegram é terceiro; fontes
visíveis; abstenção; gate institucional aberto.

**Fala:** “Sem persistência não significa sem tratamento. O Telegram recebe a
mensagem, e qualquer uso com participantes mudaria o risco e exigiria nova decisão
institucional. Por isso a demonstração é restrita a dados sintéticos enviados por
mim.”

Limitações obrigatórias: conjunto pequeno e sintético; curadoria v3 apoiada por IA,
sem validação clínica independente; viés institucional/geográfico; OCR controlado;
mudança temporal das recomendações; componentes baseados na mesma LLM.

### 10. Conclusão

**Fala:** “O trabalho demonstrou integração local, quatro classes, abstenção,
citações rastreáveis e execução no hardware-alvo. A v3 corrigiu parte importante das
limitações da v1, mas continua sendo prova de conceito. A principal contribuição é
o sistema e o processo experimental auditável, incluindo resultados negativos e
limites explícitos.”

## Perguntas prováveis da banca

### Por que não usar milhares de notícias no RAG?

O corpus de conhecimento e o dataset de avaliação têm funções diferentes. O RAG
consulta 7.585 trechos de 80 documentos; o dataset contém alegações com gabarito e
serve para medir o sistema. Milhares de notícias sem rótulo e evidência não se tornam
automaticamente um bom conjunto de avaliação.

### Por que usar fontes oficiais pode gerar viés?

Elas oferecem rastreabilidade e atualização institucional, mas refletem seleção
editorial e contexto geográfico. O projeto registra proveniência, inclui literatura
científica e apresenta esse viés como limitação, em vez de tratar a fonte como
autoridade infalível.

### Por que a v3 não tem auditor pós-geração?

O auditor foi testado. Ele aumentou abstenção, mas reduziu macro-F1 e eliminou
previsões `MISLEADING` corretas. Na v3, segurança é obtida por rotas, abstenção,
validação de IDs e seleção de citações. Reintroduzir o auditor sem nova evidência
contrariaria os resultados experimentais.

### A macro-F1 de 0,846 prova que o sistema funciona na internet?

Não. Ela vale para 32 alegações sintéticas de oito famílias novas no protocolo
confirmatório. Sustenta integração acadêmica e comparação interna com a v1, não
generalização populacional, validação clínica ou implantação pública.

### A LLM pode inventar fontes?

Ela pode tentar retornar um identificador inválido, mas a aplicação aceita somente
IDs presentes nos candidatos recuperados. As referências exibidas são construídas
programaticamente a partir do corpus. Isso reduz invenção de links, embora não
garanta que o trecho escolhido seja o melhor.

### Por que Telegram em vez de WhatsApp?

Telegram permitiu bot gratuito, long polling local e configuração individual, sem
servidor público. WhatsApp traria verificação, dependências comerciais e limites
operacionais incompatíveis com o prazo e orçamento. O Telegram ainda trata as
mensagens e isso é explicitado na análise de privacidade.

### Por que não vídeo?

Vídeo exige transcrição, seleção temporal de quadros, OCR, sincronização e novos
limites de tamanho e direitos. Isso ampliaria arquitetura e avaliação de modo
desproporcional. Foi mantido como trabalho futuro.

### Como a LGPD foi considerada?

O sistema minimiza dados, processa localmente e não persiste interações ou IDs. Logs
não carregam conteúdo. Entretanto, o tratamento transitório e a participação do
Telegram permanecem. Controlador, base legal, canal do titular e CEP/CONEP dependem
de decisão institucional e estão declarados como pendência.

### Por que a revisão humana é limitada?

Houve revisão documental e rastreabilidade, mas a confirmação v3 não teve validação
clínica independente. O trabalho não oculta essa limitação. Uma avaliação externa
maior é trabalho futuro e condição para qualquer alegação de uso público.

## Checklist de fala

- não dizer “detecta fake news” sem qualificar corpus e classes;
- não chamar macro-F1 de “porcentagem de acerto”;
- não comparar diretamente métricas de conjuntos diferentes;
- não afirmar anonimato: dizer “sem persistência local de interações”;
- não afirmar aprovação LGPD, CEP ou validação clínica;
- não prometer dois segundos para resposta completa;
- não usar mensagens reais, exemplos da banca ou token na tela;
- terminar com contribuição, limitações e trabalho futuro.
