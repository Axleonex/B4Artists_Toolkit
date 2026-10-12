# Ferramentas do CATS

[← Sumário](index.md)

As ferramentas do CATS ficam na aba **CATS** da barra lateral da direita (pressione **N**), na seção **CATS**, e sempre na aba **Cena** do editor de **Propriedades**. Elas seguem o pipeline descrito em [O pipeline do CATS](04-cats-pipeline.md). Escolha no topo da seção a armadura com que elas trabalham.

---

## Corrigir Modelo

**Fase do pipeline:** 1 (sempre a primeira)

**O que faz:** uma limpeza de um clique antes de qualquer outra operação do CATS. Ela remove problemas ocultos que, de outra forma, quebrariam em silêncio cada passo seguinte.

**Opções (cada uma pode ser desativada):**
- Aplicar modificadores
- Remover duplicados — mesclar vértices duplicados na mesma posição
- Recalcular normais — corrigir superfícies do avesso
- Remover geometria solta — faces que não estão ligadas ao corpo
- Remover grupos de vértices vazios
- Remover ossos de peso zero — ossos que não movem nenhum vértice
- Remover restrições e corpos rígidos que o VRChat não pode usar

Clique em **Corrigir Modelo** para executá-las na malha selecionada de uma vez.

---

## Traduzir Nomes de Ossos

**O que faz:** traduz os nomes de ossos do seu esqueleto para nomes do VRChat em inglês. Funciona offline, a partir de um dicionário embutido de nomes de ossos conhecidos.

**Idiomas suportados:** japonês (日本語, o mais comum, vindo do MMD e de muitos modelos da comunidade), chinês (中文), coreano (한국어), português, espanhol (Español) e francês (Français).

**Controles principais:** o **Idioma** dos nomes de origem e o botão de tradução (**Traduzir Nomes de Ossos**).

Trata-se do idioma dos nomes de ossos do modelo, não do idioma da sua interface: para um modelo MMD japonês, use-o qualquer que seja o idioma do Bforartists.

---

## Unir Malhas

**O que faz:** combina os objetos de malha do seu avatar em uma só malha. O VRChat funciona melhor com uma malha por avatar. Quando as malhas têm shape keys diferentes, o CATS completa os que faltam com formas neutras, então a malha unida tem um único conjunto coerente.

**Controles principais:** a lista de malhas (atualize-a com o botão ao lado) e depois **Unir Malhas**.

**Quando usar:** depois que todas as roupas e acessórios estiverem anexados e com pesos, e depois de Corrigir Modelo. Unir antes de Corrigir Modelo espalha os problemas de vértices duplicados de um objeto para outro; a malha unida fica então com vértices fantasmas de cada objeto original, e os visemas gerados a rasgam nas emendas.

---

## Combinador de atlas de materiais

**Fase do pipeline:** 2 (opcional)

**O que faz:** faz o bake de vários materiais em uma única folha de textura (um atlas). Menos materiais dão uma classificação de desempenho melhor no VRChat.

**Controles principais:**
- **Analyze** (analisar) — lista seus materiais e texturas, com diagnósticos, grupos de duplicados e tamanhos forçados. Escolha quais materiais e quais texturas incluir: desmarque os que você quer manter como estão.
- **Smart Combine Materials** (combinação inteligente de materiais) — o caminho recomendado: faz o bake do atlas e faz cada malha apontar para ele; o UV do atlas vira o UV0 da exportação
- **Assar Atlas** — um bake simples; **Add Group** (adicionar grupo) e **Remove Group** (remover grupo) fazem o bake de grupos de materiais separadamente
- Substituir Configurações Herdadas — tamanho do atlas, método e semente de UV, preset de empacotamento, margem do bake, passo de rotação das ilhas e passadas de bake (Albedo por padrão; Normal, Emission e Roughness podem ser feitas como saídas separadas)
- **Preserve Backup Duplicate** (manter duplicata de backup) — mantém uma cópia dos originais
- **Aceitar — Excluir Backup** — mantém o resultado e apaga o backup
- **Reverter — Restaurar Originais** — volta aos materiais originais
- **Copy Debug Report** (copiar relatório de depuração) — copia os diagnósticos para a área de transferência, para um relatório de bug

Os materiais VRM / MToon mantêm a transparência: o modo alfa é respeitado e comparado com o alfa real da textura, a emissão não estoura, e os blocos com problema são marcados em magenta depois do bake.

**Linhagem e créditos:** este fluxo de trabalho continua a linhagem de integração do CATS, dá crédito ao Cats Blender Plugin original, dá crédito ao Grim-es/material-combiner-addon pela linhagem do Material Combiner, e dá crédito ao UV Toolkit de Alexander Belyakov e ao repositório de arquivo oRazeD/UVToolkit pela inspiração do fluxo de trabalho de UV. O BoneCraft implementa suas próprias ajudas de UV para atlas em vez de incluir o código-fonte do UVToolkit.

---

## Visemas

**Fase do pipeline:** 3

**O que faz:** cria os 15 visemas do VRChat a partir de três formas base de boca.

**Controles principais:** **Forma A**, **Forma O** e **Forma CH** (escolha-as, ou use **Detecção Automática**), uma opção para sobrescrever os visemas existentes e **Gerar Visemas**. Veja o [guia 13, fase 2](03-guides-b.md#fase-2--geração-de-visemas).

---

## Rastreamento Ocular

**Fase do pipeline:** 4 (executar depois de Corrigir Modelo)

Sem Corrigir Modelo antes, a detecção dos olhos pode se prender a geometria duplicada que sobrou em vez dos olhos reais e colocar as restrições no vazio: os avatares chegam ao VRChat encarando o chão.

**O que faz:** encontra os ossos dos olhos do seu avatar, dá a eles os nomes que o VRChat exige (`LeftEye` e `RightEye`) e cria as restrições de rotação que movem os olhos naturalmente no VRChat.

**Controles principais:**
- **Detecção Automática** — encontra ossos que correspondem aos nomes e posições de ossos dos olhos
- **Olho Esquerdo** e **Olho Direito** — os ossos dos olhos, se você mesmo os escolher
- **Limite Superior**, **Limite Inferior** e **Limite Lateral** — quanto os olhos podem girar
- **Criar Rastreamento Ocular** — renomeia os ossos e cria as restrições

---

## Pose e Shape Keys

**Fase do pipeline:** 5 (opcional)

### Pose para Shape Key

Transforma a pose atual em um novo shape key, para expressões personalizadas ou uma forma de descanso corrigida. Faça a pose da armadura no Modo Pose, volte ao Modo Objeto, depois clique em **Pose para Shape Key** e dê um nome ao shape key.

### Shape Key para Basis

O inverso: faz o bake de um shape key na forma de descanso neutra da malha. Use para fixar de vez uma pose de descanso corrigida. Execute também depois de Corrigir Modelo.

---

## Transformes e FBT

**Fase do pipeline:** 6 (a última)

### Aplicar Todos os Transformes

Aplica posição, rotação e escala à malha e à armadura juntas, para que tudo seja lido com valores limpos. O SDK do VRChat precisa disso: uma escala não aplicada deixa os avatares com o tamanho errado no VRChat.

### Corrigir FBT

Uma correção de transformação para configurações de Full Body Tracking: move o osso raiz para o nível do chão.

### Remover FBT

Remove de novo a correção de Corrigir FBT.

---

## Ferramentas de Ossos

- **Criar Osso Raiz** — adiciona um osso raiz (com o nome de **Nome da Raiz**) na base da hierarquia
- **Mesclar Ossos** — mescla nos pais os ossos mais curtos que o **Limite de Mesclagem**
- **Duplicar Ossos** — duplica os ossos selecionados

---

## Ferramentas de Armadura

**O que faz:** mescla uma armadura em outra, por exemplo a armadura de uma roupa na do corpo.

**Controles principais:**
- **Base / Root** (base / raiz) — a armadura que fica (o resultado mantém o nome dela)
- **Incoming** (entrante) — a armadura que é mesclada nela; ossos com o mesmo nome se juntam à base
- Naming Prep (preparação de nomes) — faz os nomes de ossos dos dois rigs coincidirem antes da mesclagem. Funciona com qualquer rig, não só com importações do Mixamo: escolha Mixamo Prefixed e clique em **Normalize Merge Names** (normalizar nomes para mesclagem), depois escolha Mixamo Stripped e normalize de novo; os dois rigs terminam com os mesmos nomes.
- Opções para definir os pais dos ossos automaticamente e para unir as malhas depois
- **Merge Incoming Into Base** (mesclar a entrante na base) — mescla

Para uma mesclagem em etapas com pré-visualizações, use Mesclagem de Ossos na aba BoneCraft (veja [Construtor de Rig](06-rig-builder.md#mesclagem-de-ossos)).

---

## Ferramentas de Malha

- **Separar por Materiais** — uma malha por material
- **Separar por Partes Soltas** — uma malha por peça conectada
- **Separar por Shape Keys** — separa as partes que os shape keys movem

---

## Smart Automatic Weights (pesos automáticos inteligentes)

Recalcula os pesos da malha a partir do rig existente: **Smart Automatic Weights**, com **Advanced Recalculation** (recálculo avançado) para todas as configurações. A mesma ferramenta está na aba BoneCraft (Skin → Ferramentas de Peso), descrita em [Ferramentas de rig](05-rig-tools.md#recálculo-automático-de-pesos-de-ossos).

---

## Status do Pipeline e Registro de Operações

O Status do Pipeline mostra quais das seis fases estão feitas. O Registro de Operações lista cada operação do CATS com a hora e o resultado (Changed, Clean ou Failed); **Copiar** o coloca na área de transferência e **Limpar** o esvazia. Veja [O pipeline do CATS](04-cats-pipeline.md).

Próximo: [Soluções rápidas e glossário](10-reference.md)
