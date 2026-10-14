# Manuscrito-base do TCC

> Documento editável, ainda não diagramado no template institucional. Substituir
> somente os campos entre colchetes e adaptar elementos pré-textuais às regras
> fornecidas pela UNIPÊ. Não remover limitações metodológicas para reduzir páginas.

## Elementos de identificação

**Instituição:** Centro Universitário de João Pessoa — UNIPÊ  
**Curso:** Ciência da Computação  
**Autor:** [NOME COMPLETO DO AUTOR]  
**Orientador:** [NOME E TITULAÇÃO DO ORIENTADOR]  
**Cidade:** João Pessoa — PB  
**Ano:** 2026

## Título proposto

**ImmunoCheck: verificação local de alegações sobre vacinação humana com modelos de
linguagem, recuperação aumentada e fontes rastreáveis**

## Resumo

A circulação de informações falsas ou descontextualizadas sobre vacinação pode
prejudicar decisões individuais e respostas de saúde pública. Ao mesmo tempo,
modelos de linguagem de grande porte podem produzir respostas plausíveis sem
fundamentação verificável, o que limita seu uso isolado em domínios sensíveis. Este
trabalho apresenta o ImmunoCheck, um protótipo acadêmico, gratuito e executado
localmente para analisar alegações sobre vacinação humana recebidas como texto,
imagem predominantemente textual ou link HTTPS. A solução combina extração da
alegação principal, recuperação semântica sobre um corpus versionado, roteamento por
estrutura argumentativa, geração local de vereditos e seleção hierárquica de
citações. A saída distingue alegações sustentadas, refutadas, enganosas e casos de
evidência insuficiente, acompanhando a decisão com fontes construídas a partir dos
metadados reais do corpus. O desenvolvimento adotou avaliações incrementais de
recuperação, classificação, abstenção, citação, latência e recursos. A primeira
configuração, avaliada uma única vez em 64 itens congelados, obteve macro-F1 de
0,416 e não reconheceu itens enganosos. Uma configuração posterior, congelada e
confirmada em 32 itens de oito famílias novas, alcançou macro-F1 de 0,846, acurácia
de 0,844, recall de 0,625 para alegações enganosas, precisão de abstenção de 1,000,
acerto de citação por identificador de 0,833 e P95 textual de 19,35 segundos. O
protótipo operou no computador doméstico de referência e integrou texto, OCR, links
e Telegram sem persistir interações. Os resultados demonstram viabilidade técnica
para uma prova de conceito, mas não autorizam uso clínico ou implantação pública,
principalmente pela amostra sintética pequena, curadoria sem validação clínica
independente e dependência de fontes institucionais.

**Palavras-chave:** recuperação aumentada por geração; modelos de linguagem;
recuperação de informação; vacinação; desinformação em saúde; inteligência
artificial responsável.

## Abstract

False or decontextualized information about vaccination can impair individual
decisions and public-health responses. At the same time, large language models may
produce plausible answers without verifiable grounding, which limits their isolated
use in sensitive domains. This work presents ImmunoCheck, a free, locally executed
academic prototype for analysing human-vaccination claims received as text,
text-oriented images, or HTTPS links. The solution combines main-claim extraction,
semantic retrieval over a versioned corpus, routing by argumentative structure,
local verdict generation, and hierarchical citation selection. Its output
distinguishes supported, refuted, misleading, and insufficient-evidence claims and
links each decision to references built from actual corpus metadata. Development
used incremental evaluations of retrieval, classification, abstention, citation,
latency, and resource use. The first configuration, evaluated once on 64 frozen
items, achieved a macro-F1 of 0.416 and failed to identify misleading items. A
later frozen configuration, confirmed on 32 items from eight new families, achieved
a macro-F1 of 0.846, accuracy of 0.844, misleading-class recall of 0.625,
abstention precision of 1.000, exact citation accuracy of 0.833, and textual P95
latency of 19.35 seconds. The prototype ran on the reference home computer and
integrated text, OCR, links, and Telegram without persisting interactions. Results
support the technical feasibility of an academic proof of concept, but do not
authorize clinical use or public deployment, particularly because of the small
synthetic sample, the lack of independent clinical validation, and reliance on
institutional sources.

**Keywords:** retrieval-augmented generation; large language models; information
retrieval; vaccination; health misinformation; responsible artificial intelligence.

# 1 Introdução

Ambientes digitais permitem que informações de saúde circulem com grande rapidez,
mas a mesma infraestrutura também amplia mensagens falsas, imprecisas ou retiradas
de contexto. A Organização Mundial da Saúde caracteriza a desinformação em saúde
como um risco informacional e destaca que campanhas desse tipo podem enfraquecer a
confiança em instituições e intervenções, inclusive a vacinação (OMS, 2024).

A checagem desse conteúdo é difícil por pelo menos três motivos. Primeiro, uma
afirmação pode combinar uma premissa verdadeira com uma conclusão exagerada.
Segundo, recomendações de vacinação dependem de produto, população, dose, período e
contexto. Terceiro, uma resposta correta precisa ser verificável por quem a recebe,
e não apenas apresentada como autoridade do sistema.

Modelos de linguagem oferecem uma interface conveniente para interpretar linguagem
natural, porém o conhecimento armazenado em seus parâmetros não garante atualização,
proveniência ou fidelidade factual. A geração aumentada por recuperação, conhecida
como RAG, combina memória paramétrica com uma coleção documental externa e permite
inspecionar os trechos fornecidos ao gerador (LEWIS et al., 2020). Essa propriedade
é relevante para saúde, embora a presença de documentos recuperados não elimine
erros de seleção, interpretação ou citação.

Este trabalho propõe o ImmunoCheck, um protótipo que executa localmente modelos de
embedding e linguagem e usa um corpus curado de fontes oficiais e científicas sobre
vacinação humana. O sistema recebe texto, imagem textual ou link por Telegram,
produz um veredito em quatro classes, apresenta uma explicação curta e exibe fontes
rastreáveis. O desenho também incorpora abstenção, minimização de dados e limites de
uso desde a arquitetura.

## 1.1 Problema de pesquisa

Em que medida uma pipeline RAG totalmente local consegue classificar alegações sobre
vacinação humana em português, abster-se quando a evidência é insuficiente e
apresentar fontes rastreáveis no hardware doméstico?

A pergunta experimental inicial, preservada no protocolo do projeto, investigou
especificamente recuperação híbrida e verificação pós-geração. Os resultados
negativos dessas hipóteses motivaram uma linha posterior, com novos dados, baseada
em roteamento e seleção hierárquica de citações. Essa evolução foi registrada antes
de cada execução confirmatória e não alterou o teste histórico.

## 1.2 Objetivos

O objetivo geral é desenvolver e avaliar um protótipo local, gratuito e rastreável
para apoio à verificação documental de conteúdos sobre vacinação humana.

São objetivos específicos:

a) construir um corpus versionado de fontes oficiais e científicas;  
b) comparar estratégias locais de recuperação;  
c) distinguir sustentação, refutação, distorção parcial e insuficiência;  
d) apresentar referências provenientes de metadados reais;  
e) integrar texto, OCR e extração segura de links a uma interface de chat;  
f) medir qualidade, latência, consumo de recursos e falhas; e  
g) incorporar privacidade, ética, transparência e possibilidade de contestação.

## 1.3 Escopo

A primeira versão aceita mensagens de texto com até 4.096 caracteres, uma imagem
PNG, JPEG ou WebP de até 10 MB e 12 megapixels, ou uma URL HTTPS pública. Vídeo,
áudio, WhatsApp, memória conversacional, aconselhamento médico, fine-tuning,
hospedagem permanente e atualização automática do corpus ficam fora do escopo. Se
houver várias alegações, apenas a principal é analisada e essa limitação é informada.

# 2 Fundamentação teórica

## 2.1 Desinformação em saúde e vacinação

A OMS diferencia informação incorreta compartilhada sem intenção de enganar de
desinformação produzida ou difundida deliberadamente. Para o sistema proposto, a
intenção do autor não é inferida: o objeto de análise é a compatibilidade da alegação
com a evidência documental. Essa escolha reduz o risco de atribuir motivação a uma
pessoa e permite uma linguagem não punitiva.

A classe `MISLEADING` foi incluída porque conteúdos problemáticos podem preservar
uma parcela verdadeira e distorcer causalidade, alcance, frequência ou certeza. Um
classificador apenas binário tenderia a apagar essa diferença. A classe
`INSUFFICIENT_EVIDENCE`, por sua vez, evita tratar ausência de prova como falsidade.

## 2.2 Recuperação de informação

BM25 é uma função de ranqueamento lexical derivada do modelo probabilístico de
relevância e permanece uma referência para busca textual (ROBERTSON; ZARAGOZA,
2009). Métodos densos representam consultas e documentos em um espaço vetorial,
permitindo recuperar proximidade semântica mesmo quando o vocabulário não coincide.

O BGE-M3 foi escolhido como candidato multilíngue. O modelo suporta recuperação
densa, esparsa e multivetorial, mais de cem idiomas e entradas longas (CHEN et al.,
2024). O projeto usou sua representação densa com embeddings de 1.024 dimensões.

A Reciprocal Rank Fusion combina rankings sem exigir que suas pontuações originais
sejam comparáveis (CORMACK; CLARKE; BÜTTCHER, 2009). BM25, recuperação densa, RRF e
reranking foram comparados empiricamente; a arquitetura final não foi escolhida por
popularidade, mas pelo comportamento observado nos conjuntos de desenvolvimento.

## 2.3 Geração aumentada por recuperação

RAG associa um modelo gerador a uma memória documental externa recuperável. Lewis et
al. (2020) destacam a possibilidade de atualizar e inspecionar essa memória, em
contraste com o uso exclusivo do conhecimento paramétrico. No ImmunoCheck, entretanto,
o corpus recuperado não é considerado automaticamente suficiente: a aplicação valida
IDs, permite abstenção e constrói referências fora da LLM.

## 2.4 Modelos de linguagem locais

O Qwen3 reúne modelos densos e mixture-of-experts em diferentes escalas e inclui
suporte multilíngue e modos de raciocínio controláveis (YANG et al., 2025). Foi usada
a variante Qwen3-8B quantizada, executada pelo Ollama, por caber na RTX 4060 de 8 GB
e possuir licença compatível com o projeto. Nenhuma entrada de usuário é enviada a
uma LLM externa.

## 2.5 Privacidade e IA responsável

A ausência de persistência não elimina o tratamento de dados. A LGPD define
princípios como finalidade, necessidade, transparência, segurança, prevenção e não
discriminação (BRASIL, 2018). O guia da ANPD para fins acadêmicos reforça que o
contexto educacional não dispensa a avaliação das hipóteses legais e das
responsabilidades dos agentes (ANPD, 2024).

O projeto adota processamento local, logs sem conteúdo ou identificadores, fontes
visíveis, abstenção e aviso de que a resposta não substitui profissional de saúde.
O Telegram recebe a mensagem antes do computador local; portanto, a participação de
terceiro e eventual transferência internacional não podem ser ocultadas.

# 3 Metodologia

## 3.1 Caracterização da pesquisa

O trabalho é aplicado, de caráter tecnológico e experimental. Seu produto é um
artefato de software avaliado por métricas quantitativas e análise qualitativa de
erros. O processo foi incremental: decisões, hipóteses, gates, hashes e resultados
negativos foram versionados para reduzir seleção retrospectiva de resultados.

## 3.2 Ambiente

O computador de referência possui Ryzen 5 7500F, 32 GB de RAM DDR5 e GPU RTX 4060
de 8 GB. O ambiente usa Windows 11, Python 3.12, Ollama, Qwen3-8B, BGE-M3 em CPU,
Tesseract, OpenCV e Telegram Bot API por long polling. Todas as ferramentas do
caminho online são gratuitas e executadas localmente, exceto o transporte da
mensagem pelo próprio Telegram.

## 3.3 Corpus

O corpus ativo possui 80 documentos e 7.585 chunks. Foram priorizados Ministério
da Saúde, Programa Nacional de Imunizações, Anvisa, OMS, OPAS e literatura
científica selecionada. Cada entrada registra título, instituição, URL, data,
condição de uso, hash e estado de revisão. Documentos de checagem não fornecem a
resposta pronta para alegações derivadas deles.

O processamento extrai texto, preserva contexto hierárquico, segmenta documentos e
gera embeddings BGE-M3. O corpus bruto, os pesos e o índice não são versionados no
Git por licenciamento e tamanho; catálogo, receitas, hashes e relatórios são
versionados.

## 3.4 Conjuntos de avaliação

A avaliação histórica da v1 usou 160 alegações sintéticas, com 96 itens de
desenvolvimento e 64 de teste congelado. Famílias de alegações foram mantidas no
mesmo split para reduzir vazamento por paráfrase. O teste foi executado uma única
vez e não orientou alterações posteriores.

A linha v3 foi calibrada em dados separados, congelada e confirmada uma única vez
em 32 itens balanceados de oito famílias novas. O teste histórico da v1 não foi
carregado nessa confirmação. O gabarito v3 foi curado pelo pesquisador com apoio de
IA e evidência rastreável, sem validação clínica independente; essa é uma ameaça à
validade, não uma revisão especializada.

## 3.5 Métricas

Para recuperação foram usados Recall@k, MRR e nDCG@10. A avaliação fim a fim usou
acurácia, macro-F1, precisão, recall e F1 por classe, matriz de confusão, precisão
de abstenção, acerto de citação por ID, taxa de falha e latência. Intervalos de 95%
foram estimados por bootstrap por família quando previstos.

## 3.6 Procedimento experimental

Os experimentos compararam BM25, BGE-M3 denso, fusão RRF e reranking. Em seguida,
foram avaliadas pipelines completas com e sem auditoria. A v2 foi encerrada sem
promoção quando nenhuma candidata satisfez os gates. A v3 introduziu três rotas:

- proposição simples: decisão direta sobre os seis primeiros trechos;
- premissa-conclusão: decisão relacional sobre quinze trechos;
- evento específico sem âncora documental: abstenção.

Decisões conclusivas passam por uma seleção inicial de até três fontes, expansão de
chunks do mesmo documento e seleção final. Esses estágios não podem alterar o
veredito. IDs inexistentes são rejeitados, e títulos, URLs, datas e páginas são
preenchidos programaticamente.

# 4 Desenvolvimento do sistema

## 4.1 Entradas e normalização

Texto é normalizado diretamente. Imagens são validadas por tipo, dimensão e tamanho,
pré-processadas em memória e submetidas ao Tesseract. Links aceitam somente HTTPS,
bloqueiam destinos privados, revalidam redirecionamentos, limitam tempo e bytes e
extraem HTML, texto ou PDF textual. Vídeo e áudio recebem recusa explícita.

## 4.2 Extração e recuperação

Uma chamada estruturada identifica a alegação factual principal e informa a presença
de múltiplas alegações. O texto extraído é convertido em embedding e comparado por
cosseno aos chunks. A busca retorna quinze candidatos na v3. Embora o reranker tenha
melhorado nDCG@10 isoladamente, seu ganho não se converteu em melhor classificação
fim a fim e adicionou custo; por isso não integra o caminho padrão.

## 4.3 Roteamento, decisão e citação

O roteador analisa a forma, não a veracidade. Alegações simples usam o decisor direto;
relações entre premissa e conclusão usam um decisor que explicita escopo, premissa e
extrapolação; eventos individuais sem âncora recebem evidência insuficiente. Uma
seleção hierárquica posterior busca a passagem que melhor justifica a decisão.

O veredito pertence a `SUPPORTED`, `REFUTED`, `MISLEADING` ou
`INSUFFICIENT_EVIDENCE`. Para refutação, a resposta pode incluir o fato correto;
para distorção, informa o elemento omitido ou exagerado. Toda resposta inclui aviso
de que não oferece orientação médica.

## 4.4 Telegram e ausência de estado

O bot usa long polling e não requer servidor público. Conteúdo, URL, imagem,
identificadores e resposta permanecem apenas em memória durante o atendimento. A
fila e o offset também são efêmeros. Logs contêm somente categorias técnicas e
latência, sem interpolar dados da mensagem.

# 5 Resultados

## 5.1 Recuperação

Em 72 consultas conclusivas de desenvolvimento, BGE-M3 denso atingiu nDCG@10 de
0,461, contra 0,365 do híbrido RRF. O híbrido seguido de reranking alcançou 0,615,
mas o reranking apresentou mediana aproximada de 10 segundos em CPU. Nos testes fim
a fim, esse custo não trouxe melhora suficiente de classificação; BGE-M3 denso foi
mantido no caminho online.

## 5.2 Teste histórico da v1

A v1 congelada foi executada em 64 itens. Obteve macro-F1 de 0,416, acurácia de
0,469, recall de abstenção de 0,750, precisão de abstenção de 0,308, recall zero
para `MISLEADING`, latência mediana de 9,43 segundos e P95 de 12,42 segundos, sem
falhas técnicas. O sistema produziu 39 abstenções, das quais 12 eram esperadas.

Esse resultado mostrou integração funcional e comportamento conservador, mas também
excesso de abstenções e incapacidade de reconhecer distorções parciais. Nenhuma
alteração posterior usou o teste de 64 itens como conjunto de desenvolvimento.

## 5.3 Confirmação da v3

Na confirmação com 32 itens, a v3 obteve 27 acertos, acurácia de 0,844 e macro-F1
de 0,846. A v1, executada como comparação nos mesmos itens novos, obteve acurácia
de 0,531 e macro-F1 de 0,482. O ganho pareado de macro-F1 foi 0,364, com intervalo
percentil de 95% entre 0,192 e 0,540.

| Classe | Recall v3 | Acertos |
|---|---:|---:|
| `SUPPORTED` | 1,000 | 8/8 |
| `REFUTED` | 0,875 | 7/8 |
| `MISLEADING` | 0,625 | 5/8 |
| `INSUFFICIENT_EVIDENCE` | 0,875 | 7/8 |

A precisão de abstenção foi 1,000: as sete abstenções produzidas eram esperadas. A
citação exata foi correta em 20 dos 24 itens conclusivos, ou 0,833. Não houve falha
técnica. A latência mediana foi 13,78 segundos e o P95 foi 19,35 segundos. Os oito
gates pré-registrados foram satisfeitos.

Cinco erros permaneceram: três distorções foram tratadas como refutação, uma
refutação foi tratada como distorção e um evento individual sem âncora foi refutado
em vez de receber abstenção. Eles não foram usados para ajustar a candidata
confirmada.

## 5.4 Desempenho multimodal e integração

O benchmark operacional histórico executou 30 imagens, 30 links e 30 confirmações
locais, sem falhas. O P95 foi de 10,29 segundos para imagem, 9,07 segundos para link
e 0,015 milissegundo para o feedback local. O pico conservador do sistema foi 20,28
GiB de RAM e 6,83 GiB de VRAM.

Após a integração da v3, um ensaio estrutural aprovou texto, imagem com OCR real,
link controlado e rejeição de vídeo. Os fluxos aceitos levaram 19,29, 15,71 e 13,03
segundos, respectivamente. Essa pequena bateria valida o caminho atual, não substitui
o benchmark de desempenho nem estima acurácia.

## 5.5 Rastreabilidade dos resultados

Os números deste capítulo não foram recalculados durante a redação. Eles foram
transcritos dos artefatos versionados abaixo, que preservam configuração, protocolo,
saída e limitações:

| Resultado usado no texto | Artefato autoritativo |
|---|---|
| teste histórico da v1 | `evaluation/results/test/FINAL_TEST_REPORT.md` |
| recuperação e escolha do BGE-M3 | `evaluation/results/development/README.md` |
| encerramento da linha v2 | `evaluation/refinement_v2/CONSOLIDATION_REPORT.md` |
| confirmação comparativa v1 × v3 | `evaluation/refinement_v3/confirmatory/RESULTS.md` |
| latência e uso de RAM/VRAM | `evaluation/results/performance/OPERATIONAL_PERFORMANCE_REPORT.md` |
| ensaio multimodal após integração | `docs/V3_INTEGRATION.md` |

Essa separação permite corrigir a redação sem modificar evidência experimental e
evita que métricas provenientes de amostras diferentes sejam combinadas como se
fossem uma única avaliação.

## 5.6 Linha experimental v4 (resultado negativo)

Para reduzir a dependência de moldes de redação do confirmatório de 32 itens, construiu-se um
conjunto v4 com 96 itens e 24 famílias (48 de calibração e 48 de holdout lacrado). Um baseline
lexical TF-IDF reprovou o gate de atalhos na primeira redação (macro-F1 0,558) e passou após
reescrita de 47 alegações (0,328); ambas as execuções foram preservadas.

Na calibração, a v3 obteve macro-F1 0,450, contra 0,846 no confirmatório anterior, com recall
zero de `MISLEADING`. Foram testadas: métricas de retrieval por documento (denso top 15 não foi
superado por BM25, híbrido RRF ou reranker, com Doc-Recall@15 de 0,93); ancoragem verificável
D1 (macro-F1 0,542); limiares de abstenção D2 (ganho aninhado de +0,030, IC incluindo zero); e
um caminho dedicado a `MISLEADING` (recall 0,67, porém com perda de recall em `REFUTED` e
`SUPPORTED`, reprovado por 0,009 num critério pré-registrado).

A candidata v4 (v3 + D1) foi congelada e executada uma única vez no holdout. Obteve macro-F1 0,487
contra 0,577 da v3 (diferença −0,089; IC 95% por família −0,194 a +0,008) e falhou quatro dos oito
gates pré-registrados (ganho, precisão das conclusões, queda de recall de `REFUTED` e citação).
Portanto a v3 permanece a configuração do protótipo. O resultado negativo é relatado integralmente em
`evaluation/refinement_v4/HOLDOUT_RESULTS.md`.

# 6 Discussão

Os resultados mostram que qualidade de retrieval isolada não determina o desempenho
do sistema completo. O reranker melhorou nDCG, mas custo e interação com o gerador
não justificaram sua adoção. De modo semelhante, o auditor da v1 aumentou abstenção,
mas suprimiu conclusões corretas e não reconheceu `MISLEADING` no teste histórico.

A melhoria da v3 veio da decomposição do problema. Alegações simples e relações de
premissa-conclusão passaram a receber instruções diferentes, e eventos particulares
sem identificação pública ganharam uma regra explícita de abstenção. A citação foi
separada da decisão e recebeu contexto expandido dentro dos documentos escolhidos.

Mesmo assim, 0,846 não deve ser interpretado como acurácia esperada em notícias
reais. O conjunto é pequeno, sintético, balanceado e construído a partir do mesmo
universo documental. A diferença para a v1 no conjunto confirmatório é válida como
comparação interna; não é estimativa populacional nem comparação direta com o teste
histórico de 64 itens.

A linha v4 reforça essa cautela: no conjunto novo e mais variado, a v3 caiu para macro-F1 0,450 (calibração) e 0,577 (holdout), e uma intervenção que ajudou na calibração (ancoragem D1) piorou no holdout. Isso ilustra o otimismo de selecionar configurações em poucos itens.

## 6.1 Ameaças à validade

**Validade interna:** preparação dos dados pelo pesquisador, apoio de IA na curadoria
e conhecimento da arquitetura podem introduzir viés. Congelamento, hashes, famílias
novas e execução única reduzem, mas não eliminam, esse risco.

**Validade de construto:** o rótulo `MISLEADING` envolve contexto e materialidade.
Acerto de citação por ID penaliza outro chunk pertinente do mesmo documento, mas foi
mantido por ser um critério conservador.

**Validade externa:** alegações sintéticas, fontes majoritariamente oficiais,
português, imagens tipográficas e links controlados não representam toda a internet,
outras culturas, fotos difíceis ou mudanças futuras nas recomendações.

**Validade de conclusão:** amostras pequenas ampliam incerteza (o holdout v4 tem 48 itens e 12 famílias; o v4 não teve segunda anotação nem revisor externo). O bootstrap por
família evita tratar paráfrases como observações totalmente independentes, mas não
substitui avaliação maior e externa.

# 7 Aspectos éticos, LGPD e direitos humanos

O ImmunoCheck não deve ser apresentado como árbitro definitivo. Sua função é
comparar uma alegação com um corpus delimitado e permitir inspeção das fontes. O
usuário pode contestar a decisão; o sistema não remove publicações, identifica
autores ou aplica sanções.

A minimização é aplicada por desenho: não há conta própria, histórico, memória
conversacional ou telemetria de conteúdo. Ainda assim, texto, imagem, URL e
identificadores recebidos constituem tratamento transitório, e o Telegram pode
conservar dados segundo sua própria política. Dados sensíveis enviados por engano
não devem ser reproduzidos ou transformados em dataset.

Papéis de controlador e operador, base legal, canal do titular, transferência
internacional, procedimento de incidente e eventual enquadramento CEP/CONEP dependem
de decisão institucional. Enquanto esse gate estiver aberto, o uso fica restrito à
demonstração pelo autor com entradas sintéticas previamente definidas. Não há
autorização para piloto público ou pesquisa com participantes.

# 8 Conclusão

O trabalho entregou um protótipo local e gratuito que integra LLM, RAG, OCR, extração
segura de links, Telegram, quatro classes de veredito e fontes programáticas. A v1
demonstrou viabilidade de integração, mas revelou baixa qualidade em distorções e
abstenção excessiva. A v3 roteada, avaliada com dados novos e congelados, apresentou
melhora substancial e satisfez todos os gates de integração.

A principal contribuição não é apenas um classificador, mas um processo auditável:
corpus versionado, decisões arquiteturais registradas, resultados negativos
preservados, teste histórico selado, confirmação separada, controles de privacidade
e limites explícitos. O resultado é adequado a uma prova de conceito de graduação,
mas não a uso clínico ou público.

Como trabalhos futuros, recomendam-se avaliação com conteúdo espontâneo após
aprovação ética, revisão clínica independente, ampliação do corpus, estudo de
acessibilidade, imagens reais com diferentes níveis de qualidade, atualização
temporal das fontes e nova candidata treinada e confirmada em conjuntos ainda não
vistos. Vídeo e WhatsApp devem permanecer extensões separadas, pois alteram custo,
tratamento de dados e escopo experimental.

# Referências iniciais

AGÊNCIA NACIONAL DE PROTEÇÃO DE DADOS (ANPD). **Guia orientativo: tratamento de
dados pessoais para fins acadêmicos e para a realização de estudos e pesquisas**.
Brasília, DF: ANPD, 2024. Disponível em:
https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-tratamento-de-dados-pessoais-para-fins-academicos-e-para-a-realizacao-de-estudos-e-pesquisas.
Acesso em: 27 set. 2026.

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados
Pessoais. Brasília, DF: Presidência da República, 2018. Disponível em:
https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em:
27 set. 2026.

CHEN, Jianlv et al. M3-Embedding: multi-linguality, multi-functionality,
multi-granularity text embeddings through self-knowledge distillation. In:
**Findings of the Association for Computational Linguistics: ACL 2024**. [S. l.]:
Association for Computational Linguistics, 2024. p. 2318–2335. Disponível em:
https://aclanthology.org/2024.findings-acl.137/. Acesso em: 27 set. 2026.

CORMACK, Gordon V.; CLARKE, Charles L. A.; BÜTTCHER, Stefan. Reciprocal rank fusion
outperforms Condorcet and individual rank learning methods. In: **Proceedings of the
32nd International ACM SIGIR Conference on Research and Development in Information
Retrieval**. New York: ACM, 2009. p. 758–759. DOI: 10.1145/1571941.1572114.

LEWIS, Patrick et al. Retrieval-augmented generation for knowledge-intensive NLP
tasks. In: **Advances in Neural Information Processing Systems 33**. [S. l.]:
Curran Associates, 2020. Disponível em: https://arxiv.org/abs/2005.11401. Acesso em:
27 set. 2026.

ORGANIZAÇÃO MUNDIAL DA SAÚDE (OMS). **Disinformation and public health**. Genebra:
OMS, 2024. Disponível em:
https://www.who.int/news-room/questions-and-answers/item/disinformation-and-public-health/.
Acesso em: 27 set. 2026.

ROBERTSON, Stephen; ZARAGOZA, Hugo. The probabilistic relevance framework: BM25 and
beyond. **Foundations and Trends in Information Retrieval**, v. 3, n. 4, p. 333–389,
2009. DOI: 10.1561/1500000019.

YANG, An et al. **Qwen3 technical report**. arXiv:2505.09388, 2025. Disponível em:
https://arxiv.org/abs/2505.09388. Acesso em: 27 set. 2026.

## Pendências editoriais antes da submissão

- substituir os campos de autor e orientador;
- aplicar o template oficial da UNIPÊ quando ele for fornecido;
- confirmar título, natureza do trabalho, folha de aprovação e ficha catalográfica;
- adequar sumário, numeração, figuras, tabelas e referências à norma adotada;
- inserir capturas apenas com fixtures sintéticas e sem token ou identificadores;
- decidir com o orientador se os relatórios internos serão citados como apêndices;
- anexar ou resumir o retorno institucional LGPD/CEP, caso seja recebido;
- revisar o texto final com o orientador sem alterar retrospectivamente resultados.
