# Guias 8–13

[← Sumário](index.md)

## Guia 8: configure a sincronia labial

`CATS → VRChat Tools → Facial`

> **Tempo:** cerca de 10–20 minutos
> **Resultado:** a boca do seu avatar se movendo corretamente quando você fala no VRChat

**Antes de começar, verifique:**
- [ ] A malha da cabeça do seu avatar tem shape keys de boca (também chamados de blend shapes ou morph targets: as diferentes posições da boca para falar)
- [ ] Você sabe mais ou menos como os shape keys se chamam (veja a lista Shape Keys nas propriedades de Dados do objeto da malha)

> Visema = uma forma de boca para um som. `aa` é o som "á", `O` o som "ô", e assim por diante. O VRChat usa 15 visemas para movimentar a sincronia labial do seu avatar.
>
> Shape key (blend shape) = uma versão salva da sua malha em outra posição. Seu shape key de boca aberta é a sua malha com a boca aberta.

---

### Passo 1 — Abrir VRChat Viseme Mapping

Na aba **CATS → VRChat Tools → Facial** → VRChat Viseme Mapping.

---

### Passo 2 — Mapear os visemas automaticamente

Clique em **Mapear Todos os Visemas Automaticamente**. O BoneCraft lê os shape keys da sua malha e os associa pelo nome aos 15 slots de visemas do VRChat.

**O que você deve ver:** a lista de visemas, com a maioria dos slots mostrando um shape key mapeado.

---

### Passo 3 — Preencher os slots que faltam

Um slot sem shape key mostra "(unmapped)" (não mapeado). Clique no botão de um slot para abrir uma lista de busca com os shape keys da sua malha e escolha o mais parecido (digite para filtrar a lista). Escolha "(unmapped)" para limpar um slot. Correspondências comuns:

| Visema do VRChat | Como soa | Shape key a procurar |
|---|---|---|
| `aa` | "á" | mouth_open, A, aa |
| `O` | "ô" | mouth_o, OH, oh |
| `CH` | "tch" / "ch" | mouth_ch, CH |
| `PP` | lábios juntos (P, B, M) | mouth_m, MM, lips_together |
| `SS` | "sss" / "zzz" | mouth_s, SS |

**Nenhum shape key de visema?** Se a boca tiver pelo menos três formas base (A, O e CH), a seção **Visemas** da aba CATS cria os 15 a partir delas. Sem nenhuma forma de boca, crie primeiro essas três. Veja o [guia 13, fase 2](#fase-2--geração-de-visemas).

---

### Passo 4 — Conferir uma forma de boca

Para ver uma forma de boca mapeada, defina o valor do shape key dela como 1.0 na lista Shape Keys da malha (Propriedades → Dados do objeto) e depois volte para 0.

---

### Passo 5 — Rastreamento facial (opcional)

Abaixo da lista de visemas, **Rastreamento Facial (SteamVR)** prepara formas de expressão para hardware de rastreamento facial. É opcional: a maioria dos usuários não precisa.

**O que isso libera:** a boca do seu avatar se move quando você fala no VRChat. As expressões se apoiam nos shape keys que você acabou de mapear.

---

## Guia 9: melhore o desempenho do seu avatar

`CATS → VRChat Tools → Check Performance`

> **Tempo:** cerca de 15–25 minutos
> **Resultado:** uma classificação de desempenho melhor no VRChat e carregamento mais rápido para outros jogadores

**Antes de começar, verifique:**
- [ ] Seu avatar está pronto (com rig, com roupas, com sincronia labial configurada)
- [ ] Você sabe qual classificação quer atingir (Good ou Excellent para a maioria dos usuários)

> Classificação de desempenho = a avaliação do VRChat de quanto seu avatar exige. Avatares Very Poor podem ser ocultados por outros jogadores. Avatares Good e Excellent carregam rápido e sempre são mostrados.

---

### Passo 1 — Verificar a classificação atual

Na aba **CATS**, expanda **VRChat Tools** → **Verificar Desempenho**. Clique em **Calculate Performance Rank** (calcular classificação de desempenho). O BoneCraft mostra a classificação geral e um detalhamento (polígonos, malhas com skin, slots de material, ossos, PhysBones e contatos), com a distância de cada um até o próximo nível.

---

### Passo 2 — Limpar

O Otimizador VRChat da mesma seção lista correções seguras. O **Modo Hipotético** começa ativado: cada correção informa o que mudaria sem mudar nada. Desmarque-o, porque enquanto ele está ativo as correções só informam, e execute as correções que quiser:

1. **Remover Ossos de Peso Zero** — apaga ossos que não movem nenhuma parte da malha
2. **Mesclar Malhas do Mesmo Material** — une malhas que compartilham um material
3. **Remover Shape Keys Não Utilizados** — apaga shape keys que nada usa
4. **Remover Grupos de Vértices Não Utilizados** — remove grupos de pesos vazios

---

### Passo 3 — Reduzir o número de polígonos (se necessário)

Se o número de polígonos estiver alto demais, use a Decimação VRChat da mesma seção com a malha selecionada: defina a proporção desejada (0.5 reduz os polígonos pela metade, 0.8 remove 20%), clique em **Pré-visualizar** para ver o resultado e em **Aplicar** para mantê-lo. Os shape keys ficam protegidos durante a decimação.

> Comece em 0.8 e vá descendo: reduções pequenas raramente mudam a aparência do avatar, mas podem melhorar muito o desempenho.

---

### Passo 4 — Mesclar materiais (opcional)

Se seu avatar usa muitos materiais, combine-os em uma única folha de textura (um atlas). Na aba **CATS** → **CATS** → **Atlas de Materiais**:

1. Clique em **Analyze** (analisar) para ver seus materiais e texturas. Escolha quais incluir.
2. Clique em **Smart Combine Materials** (combinação inteligente de materiais) (ou em **Assar Atlas** para um bake simples). O BoneCraft faz o bake do atlas e faz cada malha apontar para ele; um backup dos originais é mantido.
3. Clique em **Aceitar — Excluir Backup** para manter o resultado, ou em **Reverter — Restaurar Originais** para voltar.

[Ferramentas do CATS: Combinador de atlas de materiais](09-cats.md#combinador-de-atlas-de-materiais) explica cada ajuste.

---

### Passo 5 — Verificar a classificação de novo

Clique de novo em **Calculate Performance Rank** para ver a melhora.

**O que isso libera:** uma classificação melhor significa que mais jogadores veem seu avatar. Um avatar Good ou Excellent carrega rápido, usa menos GPU e é mostrado por padrão aos outros jogadores.

---

## Guia 10: salve e reutilize poses

`BoneCraft → Review → Pose Library`

> **Tempo:** cerca de 5–10 minutos
> **Resultado:** uma biblioteca de poses salvas que você aplica com um clique

**Antes de começar, verifique:**
- [ ] Seu avatar tem um esqueleto pronto
- [ ] Você está no **Modo Pose** (selecione a armadura e pressione Ctrl+Tab, ou use o menu suspenso de modos no canto superior esquerdo da viewport)

---

### Passo 1 — Abrir a biblioteca de poses

Na aba **BoneCraft** da Tool Shelf da esquerda, expanda **Revisão** → **Biblioteca de Poses**.

---

### Passo 2 — Fazer a pose do avatar

Mova os ossos para a posição que você quer guardar: gire os braços, incline a cabeça. Qualquer combinação de posições de ossos é uma pose.

---

### Passo 3 — Salvar a pose

Clique em **Salvar** e dê um nome à pose (por exemplo "Peace Sign" ou "Thinking"). **Categoria** a coloca em um grupo como "Greetings"; o **Filtro** no topo mostra uma categoria por vez. Uma miniatura da viewport é capturada com a pose.

---

### Passo 4 — Aplicar uma pose salva

Selecione uma pose e clique em **Aplicar**.

- **Mesclar** — aplica a pose com intensidade parcial, para misturar duas poses
- **Espelhar** — aplica a pose invertida da esquerda para a direita

**Renomear** e **Excluir** gerenciam a lista.

---

### Passo 5 — Exportar e importar poses

**Exportar** salva sua biblioteca de poses em um arquivo `.bfpose` que você pode manter com o projeto ou compartilhar. **Importar** carrega poses de um arquivo `.bfpose`.

**O que isso libera:** uma biblioteca de poses própria, que você pode reutilizar entre projetos, misturar para chaves de animação ou compartilhar com outros usuários do BoneCraft.

---

## Guia 11: junte dois rigs

`BoneCraft → Setup Rigging → Bone Merge`

> **Tempo:** cerca de 25–40 minutos, conforme a complexidade
> **Resultado:** dois esqueletos combinados em um, com todos os pesos mantidos

**Antes de começar, verifique:**
- [ ] O avatar base e o segundo rig (um rig de roupa ou de acessório) estão no mesmo arquivo
- [ ] Os dois têm rig e pesos

> Juntar rigs = absorver um esqueleto dentro de outro, para terminar com um só esqueleto combinado. Útil quando um rig de corpo e um rig de cabelo ou de roupa precisam virar um só.

---

### Passo 1 — Abrir Mesclagem de Ossos

Na aba **BoneCraft → Setup Rigging**, expanda a seção **Mesclagem de Ossos**. Ela funciona em três etapas; cada uma abre quando a anterior termina.

---

### Passo 2 — Etapa 1: escopo

Escolha a armadura **Base** (o esqueleto do corpo, que fica) e a armadura que se mescla nela (o rig de roupa ou de cabelo, que é adicionado à base e depois ocultado). Clique em **Analyze** (analisar).

O BoneCraft compara os dois esqueletos e lista:
- ✓ Matched (correspondentes) — ossos que existem nos dois e estão alinhados
- \+ Source only (só origem) — ossos do rig mesclado sem correspondente na base
- − Target only (só destino) — ossos da base que o rig mesclado não tem

Depois de ler a lista, clique em **Acknowledge Scope — Proceed to Rename** (confirmar escopo — seguir para renomear).

---

### Passo 3 — Etapa 2: renomear

Para cada osso "só origem", decida o que ele é:

- Dê a ele o nome do osso da base que ele representa e clique em **Apply Rename** (aplicar renomeação)
- Clique em **Mark as Unique** (marcar como único) se for um osso novo sem equivalente (ele é adicionado à base como está)

**Normalize Both Armatures** (normalizar as duas armaduras) renomeia os ossos padrão (coluna, braços, pernas etc.) que o BoneCraft reconhece nos dois rigs. **Auto-Propose Renames** (propor renomeações automaticamente) sugere nomes para o restante a partir da posição de cada osso; **Apply Batch Pattern** (aplicar padrão em lote) renomeia muitos ossos com um só padrão.

Quando cada osso "só origem" estiver resolvido, clique em **Verify Rename — Proceed to Merge** (verificar renomeação — seguir para mesclar).

---

### Passo 4 — Etapa 3: mesclar

Clique primeiro em **Run Merge Preview** (executar pré-visualização da mesclagem): ele informa o que a mesclagem vai fazer, sem mudar nada.

Quando o relatório parecer certo, clique em **Mesclar Armaduras**. O BoneCraft faz backup das duas armaduras e depois as combina.

**O que você deve ver:** uma única armadura com todos os ossos dos dois esqueletos, e cada malha com pesos em relação a ela.

**O que isso libera:** um único rig, mais fácil de exportar e editar. Necessário para qualquer avatar com rigs separados de roupa ou acessórios.

---

## Guia 12: resolva problemas de envio

> **Tempo:** cerca de 5–15 minutos, conforme o problema

**Antes de começar:** encontre seu problema na lista abaixo e vá para essa seção.

---

### "O envio falhou — ossos não reconhecidos"

Seus ossos têm nomes que o VRChat não entende. → [Guia 4: corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar)

---

### "O avatar está em pose T / não se move comigo no VRChat"

O mapeamento humanoide está faltando ou errado. → [Guia 5: mapeie seu avatar para o sistema corporal do VRChat](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat)

---

### "A malha se deforma de um jeito estranho / a pele estica errado"

Os pesos dos ossos precisam de ajuste. → Veja a transferência de pesos e o espelhamento de pesos em [Ferramentas de rig](05-rig-tools.md), ou execute **Smart Automatic Weights** (pesos automáticos inteligentes) na aba CATS.

---

### "O cabelo atravessa a cabeça"

Os colisores de cabelo estão faltando ou são pequenos demais. → [Guia 6: adicione física de cabelo](02-guides-a.md#guia-6-adicione-física-de-cabelo), passo 5.

---

### "O avatar tem desempenho Very Poor e outros jogadores o bloqueiam"

→ [Guia 9: melhore o desempenho do seu avatar](#guia-9-melhore-o-desempenho-do-seu-avatar)

---

### "A sincronia labial não funciona"

Os visemas não estão mapeados corretamente. → [Guia 8: configure a sincronia labial](#guia-8-configure-a-sincronia-labial)

---

### "O validador de rig mostra erros"

Na aba **BoneCraft**, expanda **Revisão** → **Validador de Rig** e clique em **Executar validação**. Cada resultado nomeia o problema e o osso; siga a sugestão ou consulte o [Índice de soluções rápidas](10-reference.md#índice-de-soluções-rápidas). **Export Report** (exportar relatório) salva os resultados em um arquivo.

---

### "A importação de VRM não funciona"

Talvez o add-on VRM não esteja instalado. → [Guia 2](02-guides-a.md#guia-2-leve-um-avatar-do-vroid-para-o-vrchat), passo 1.

---

### "A importação de MMD não funciona"

Talvez o add-on mmd_tools não esteja instalado. → [Guia 3](02-guides-a.md#guia-3-leve-um-avatar-do-mmd-para-o-vrchat), passo 1.

---

## Guia 13: prepare seu avatar para o VRChat com o CATS

> **Tempo:** cerca de 20–35 minutos para uma passagem completa pelo pipeline
> **Resultado:** um avatar limpo e otimizado, com sincronia labial, rastreamento ocular e transformações corretas, pronto para enviar ao VRChat

**Antes de começar, leia isto primeiro:**

As ferramentas do CATS seguem um pipeline: cada fase precisa ser feita em ordem. O Status do Pipeline da aba CATS marca cada fase concluída (Corrigir Modelo, Atlas de Materiais, Visemas, Rastreamento Ocular, Pose para Shape Key, Aplicar transformações), e o Registro de Operações lista cada operação do CATS que você executou. Uma ferramenta cuja fase anterior não foi feita roda mesmo assim, mas mostra um aviso como "Run Fix Model first for best results" (execute primeiro Corrigir Modelo para obter os melhores resultados).

**Comece sempre com Corrigir Modelo. Todas as vezes. Sem exceção.**

Leia [O pipeline do CATS](04-cats-pipeline.md) antes de continuar, se ainda não leu.

**Antes de começar, verifique:**
- [ ] Seu avatar está importado e visível na viewport 3D
- [ ] A aba CATS está aberta na barra lateral da direita (pressione N se a barra estiver oculta)
- [ ] Seu avatar está selecionado (clique nele na viewport ou no outliner)

---

### Fase 1 — Corrigir Modelo

Corrigir Modelo é a base obrigatória de todo o resto no CATS. Execute-o primeiro, mesmo que seu modelo pareça bem: ele remove problemas ocultos que, de outra forma, quebrariam em silêncio as ferramentas seguintes.

**O que Corrigir Modelo faz** (cada parte pode ser desativada nas opções):
- Aplica os modificadores
- Remove vértices duplicados e geometria solta (triângulos flutuando longe do corpo)
- Recalcula as normais (as direções que decidem qual lado da malha fica para fora)
- Remove grupos de vértices vazios e ossos de peso zero
- Remove restrições e corpos rígidos que o VRChat não pode usar

**Passos:**
1. Na aba **CATS**, expanda **CATS** → **Corrigir Modelo**
2. Confira se a malha do seu avatar está selecionada
3. Clique em **Corrigir Modelo** e espere; em malhas grandes leva alguns segundos
4. Confira se o Status do Pipeline mostra uma marca (✓) em Corrigir Modelo

**O que você deve ver:** seu avatar fica igual ou um pouco mais limpo. O Status do Pipeline marca Corrigir Modelo, e o Registro de Operações lista a execução.

> **Se seu modelo sumir ou parecer do avesso depois de Corrigir Modelo:** as normais da malha estavam invertidas. Selecione a malha, entre no Modo Edição (Tab), selecione tudo (A) e use Malha > Normais > Inverter. Depois execute Corrigir Modelo de novo.

---

### Fase 2 — Geração de visemas

Executar depois de: Corrigir Modelo ✓

A seção Visemas cria as 15 formas de boca de sincronia labial do VRChat a partir de três formas base que você já tem. Se seu avatar já tem shape keys de visemas completos, você pode pular esta fase, mas confira-os no VRChat Viseme Mapping (guia 8).

O VRChat precisa de 15 formas de boca (visemas) para movimentar os lábios do seu avatar quando você fala. A maioria dos avatares tem só algumas formas básicas de boca. O CATS combina suas formas base para criar o resto.

As três formas base:
- **Forma A** — boca bem aberta (a forma do "á")
- **Forma O** — boca arredondada (a forma do "ô")
- **Forma CH** — boca entreaberta com os dentes à mostra (a forma do "tch" / "ch")

**Passos:**
1. Na aba **CATS**, expanda **CATS** → **Visemas**
2. Clique em **Detecção Automática** para preencher as três formas, ou escolha-as você mesmo (para chaves com nomes como `mouth_open`, `vrc.v_O` ou `mouth_wide`, escolha a mais parecida)
3. Clique em **Gerar Visemas**
4. O CATS cria 15 shape keys com os nomes do VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH` etc.)
5. Confira se o Status do Pipeline mostra Visemas ✓

**O que você deve ver:** 15 shape keys novos na lista Shape Keys da malha (Propriedades → Dados do objeto → Shape Keys).

> **Se seu avatar não tem nenhum shape key de boca:** crie você mesmo pelo menos A, O e CH (esculpa ou edite essas formas como shape keys) antes que o CATS possa gerar o resto. Veja a entrada Shape key do glossário.

---

### Fase 3 — Rastreamento Ocular

Executar depois de: Corrigir Modelo ✓

O rastreamento ocular configura os ossos dos olhos do seu avatar para o rastreamento ocular embutido do VRChat, para que os olhos se movam naturalmente e olhem para outros jogadores.

**O que ele faz:**
- Encontra os ossos do olho esquerdo e do direito
- Dá a eles os nomes que o VRChat exige (`LeftEye` e `RightEye`)
- Adiciona as restrições de rotação de que o VRChat precisa para mover os olhos
- Limita a rotação dos olhos a uma faixa natural (para cima, para baixo e para os lados)

Sem Corrigir Modelo antes, a detecção dos olhos pode se prender a vértices duplicados que sobraram em vez dos olhos reais e colocar as restrições no lugar errado: os avatares chegam ao VRChat com os dois olhos travados olhando para baixo.

**Passos:**
1. Na aba **CATS**, expanda **CATS** → **Rastreamento Ocular**
2. Clique em **Detecção Automática**; o CATS procura ossos cujo nome ou posição correspondam a ossos dos olhos
3. Confira os campos **Olho Esquerdo** e **Olho Direito**; escolha você mesmo os ossos se estiverem errados
4. Defina o **Limite Superior**, o **Limite Inferior** e o **Limite Lateral**, se necessário
5. Clique em **Criar Rastreamento Ocular**
6. Confira se o Status do Pipeline mostra Rastreamento Ocular ✓

**O que você deve ver:** os dois ossos dos olhos renomeados, com restrições de rotação no painel Restrições de osso.

> **Se o CATS não encontrar ossos dos olhos:** talvez seu esqueleto não tenha. Alguns formatos (sobretudo modelos MMD antigos) piscam com shape keys em vez de ossos. Pule esta fase: o VRChat passa a usar a animação dos olhos por shape keys quando não há ossos dos olhos.

---

### Fase 4 — Pose para Shape Key

Executar depois de: Corrigir Modelo ✓

Pose para Shape Key transforma a pose atual do seu avatar em um shape key. Use-o para capturar expressões personalizadas ou poses de descanso para o menu de expressões do VRChat.

Sem Corrigir Modelo antes, a ordem dos vértices ainda pode ter lacunas deixadas pelos duplicados removidos, e o shape key captura geometria distorcida: shape keys que fazem a malha explodir para fora quando ativados no VRChat.

**Passos:**
1. Faça a pose do seu avatar no Modo Pose (selecione a armadura, pressione Ctrl+Tab)
2. Mova os ossos para a expressão ou posição que você quer capturar
3. Volte ao Modo Objeto (Ctrl+Tab de novo)
4. Na aba **CATS**, expanda **CATS** → **Pose e Shape Keys**
5. Clique em **Pose para Shape Key** e dê um nome ao novo shape key
6. Confira se o Status do Pipeline mostra Pose para Shape Key ✓

**O que você deve ver:** um novo shape key na lista da malha. Defina o valor dele como 1.0 para conferir que ele mostra a pose.

> **Shape Key para Basis:** a ferramenta complementar faz o contrário: faz o bake de um shape key na forma de descanso neutra da malha. Use-a para fixar uma pose de descanso corrigida. Execute-a também depois de Corrigir Modelo.

---

### Fase 5 — Aplicar transformações

Executar depois de: todas as fases anteriores de que você precisa

A última fase. Aplicar transformações congela toda a posição, rotação e escala na malha e no esqueleto, para que tudo seja lido com valores limpos (posição 0,0,0 / rotação 0°,0°,0° / escala 1.0). O SDK do VRChat precisa de transformações limpas: em especial, uma escala não aplicada faz os avatares aparecerem com o tamanho errado ou com uma física que se comporta mal.

Aplicar as transformações antes das fases anteriores grava os problemas delas na malha para sempre: avatares que parecem certos no Bforartists mas aparecem no VRChat com uma fração da altura.

**As ferramentas de Transformes e FBT:**
- **Aplicar Todos os Transformes** — aplica posição, rotação e escala à malha e à armadura juntas
- **Corrigir FBT** — uma correção de transformação para configurações de Full Body Tracking (move o osso raiz para o nível do chão)
- **Remover FBT** — remove essa correção de novo

**Passos:**
1. Confirme que as fases de que seu avatar precisa estão marcadas no Status do Pipeline (Atlas de Materiais e Pose para Shape Key são opcionais, e Visemas fica desmarcado se você mapeou visemas existentes)
2. Na aba **CATS**, expanda **CATS** → **Transformes e FBT**
3. Clique em **Aplicar Todos os Transformes**
4. Confira se o Status do Pipeline mostra Aplicar transformações ✓
5. Exporte seu avatar (VRChat → Exportar para VRChat, guia 1 passo 9)

**O que você deve ver:** Aplicar transformações marcado, depois das fases de que você precisava. Seu avatar está pronto para o VRChat Creator Companion.

---

**O que isso libera:** um avatar totalmente processado, com geometria limpa, os 15 visemas, rastreamento ocular (quando tem ossos dos olhos), as expressões personalizadas que você criou e transformações limpas: tudo o que um envio ao VRChat precisa para funcionar de primeira.

Próximo: [O pipeline do CATS](04-cats-pipeline.md)
