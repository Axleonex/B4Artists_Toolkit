# Guias 8–13

[← Conteúdo](index.md)

## Guia 8: configure a sincronia labial

> **Tempo:** Cerca de 10–20 minutos
> **Resultado:** A boca do seu avatar se move corretamente quando você fala em VRChat

**Antes de começar - verifique estes:**
- [] A malha da cabeça do seu avatar possui chaves de formato de boca (também chamadas de formas de mistura ou alvos de transformação - as diferentes posições da boca para falar)
- [] Você sabe aproximadamente como são nomeadas as chaves de forma (veja a lista Chaves de Forma das propriedades de Dados do Objeto da malha)

> Viseme = formato de boca para um som. `aa` é o som "ahh", `O` o som "ohh" e assim por diante. VRChat usa 15 visemas para acionar a sincronização labial do seu avatar.
>
> Shape key (forma de mesclagem) = uma versão salva de sua malha em outra posição. Sua chave de formato de boca aberta é sua malha com a boca aberta.

---

### Passo 1 — Abrir VRChat Viseme Mapping

Na guia **CATS** na barra lateral direita, expanda**Avatar Tools** →**VRChat Viseme Mapping**.

---

### Passo 2 — Mapear os visemas automaticamente

Clique em **Auto-Map All Visemes**. BoneCraft lê as chaves de forma da sua malha e as combina com os 15 slots de visema do VRChat por nome.

**O que você deveria ver:** A lista do visema, com a maioria dos slots mostrando uma chave de forma mapeada.

---

### Passo 3 — Preencher os slots que faltam

Um slot sem shape key mostra "(não mapeado)". Clique no botão de um slot para abrir uma lista de pesquisa das chaves de forma da sua malha e escolha a mais próxima (digite para filtrar a lista). Escolha "(não mapeado)" para limpar um slot. Correspondências comuns:

|VRChat visema|Como parece|Chave de formato para procurar|
|---|---|---|
|`aa` |"ahh"|boca_aberta, A, aa|
|`O` |"ahh"|boca_o, oh, oh|
|`CH` |"ch" / "sh"|boca_ch, CH|
|`PP` |lábios juntos (P, B, M)|boca_m, MM, lábios_juntos|
|`SS` |"sss" / "zzz"|boca_s, SS|

**Nenhuma chave de formato de visema?** Se a boca tiver pelo menos três formatos de base (A, O e CH), a seção**Visemes** da guia CATS cria todos os 15 a partir deles. Sem nenhum formato de boca, faça esses três primeiro. Consulte [Guia 13, Fase 2](#fase-2--geração-de-visemas).

---

### Passo 4 — Conferir uma forma de boca

Para ver uma forma de boca mapeada, defina o valor de sua chave de forma como 1,0 na lista Chaves de forma da malha (Propriedades → Dados do objeto) e, em seguida, defina-o novamente como 0.

---

### Passo 5 — Rastreamento facial (opcional)

Abaixo da lista de visemas, **Face Tracking (SteamVR)** prepara formas de expressão para hardware de rastreamento facial. É opcional: a maioria dos usuários não precisa disso.

**O que isso desbloqueia:** A boca do seu avatar se move quando você fala em VRChat. As expressões são baseadas nas chaves de forma que você acabou de mapear.

---

## Guia 9: melhore o desempenho do seu avatar

> **Tempo:** Cerca de 15–25 minutos
> **Resultado:** Uma melhor classificação de desempenho VRChat e carregamento mais rápido para outros jogadores

**Antes de começar - verifique estes:**
- [] Seu avatar está completo (equipado, vestido, configuração de sincronização labial)
- [] Você conhece sua classificação alvo (Bom ou Excelente para a maioria dos usuários)

> Classificação de desempenho = classificação de VRChat sobre o nível de exigência do seu avatar. Avatares muito ruins podem ser ocultados por outros jogadores. Avatares bons e excelentes carregam rapidamente e são sempre exibidos.

---

### Passo 1 — Verificar a classificação atual

Na guia **CATS**, expanda**VRChat Tools** e encontre seu grupo Desempenho. Clique em**Calculate Performance Rank**. BoneCraft mostra a classificação geral e um detalhamento – polígonos, malhas skinned, slots de material, ossos, PhysBones e contatos – com a distância de cada um do próximo nível.

---

### Passo 2 — Limpar

O VRChat Optimizer na mesma seção lista correções seguras. **What-If Mode** está ativado inicialmente: cada correção informa o que mudaria sem alterar nada. Desmarque-o, porque as correções só são reportadas enquanto estiver ativado e execute as correções desejadas:

1. **Remove Zero-Weight Bones** — exclui ossos que não movem nenhuma parte da malha
2. **Merge Same-Material Meshes** — une malhas que compartilham um material
3. **Remove Unused Shape Keys** – exclui chaves de forma que nada usa
4. **Remove Unused Vertex Groups** — remove grupos de peso vazios

---

### Passo 3 — Reduzir o número de polígonos (se necessário)

Se a contagem de polígonos for muito alta, use VRChat Decimation na mesma seção com a malha selecionada: defina a proporção alvo (0,5 divide os polígonos pela metade, 0,8 remove 20%), clique em **Preview** para ver o resultado e em**Apply** para mantê-lo. As chaves de forma são protegidas durante a dizimação.

> Comece em 0,8 e vá descendo: pequenas reduções raramente mudam a aparência do avatar, mas podem melhorar muito o desempenho.

---

### Passo 4 — Mesclar materiais (opcional)

Se o seu avatar usa muitos materiais, combine-os em uma folha de textura (um atlas). Na guia **CATS** →**CATS** →**Material Atlas**:

1. Clique em **Analyze** para ver seus materiais e texturas. Escolha quais incluir.
2. Clique em **Smart Combine Materials** (ou**Bake Atlas** para um cozimento simples). BoneCraft prepara o atlas e aponta cada malha para ele; um backup dos originais é mantido.
3. Clique em **Accept — Delete Backup** para manter o resultado ou em**Revert — Restore Originals** para voltar.

[Ferramentas CATS: Combinador de Atlas de Materiais](09-cats.md#combinador-de-atlas-de-materiais) explica cada configuração.

---

### Passo 5 — Verificar a classificação de novo

Clique em **Calculate Performance Rank** novamente para ver a melhoria.

**O que isso desbloqueia:** Uma classificação melhor significa que mais jogadores veem seu avatar. Um avatar Bom ou Excelente carrega rapidamente, usa menos GPU e é mostrado aos outros jogadores por padrão.

---

## Guia 10: salve e reutilize poses

> **Tempo:** Cerca de 5 a 10 minutos
> **Resultado:** Uma biblioteca salva de poses que você pode aplicar com um clique

**Antes de começar - verifique estes:**
- [] Seu avatar tem um esqueleto finalizado
- [] Você está em **Pose Mode** (selecione a armadura e pressione Ctrl+Tab ou use o menu suspenso de modo no canto superior esquerdo da janela de visualização)

---

### Passo 1 — Abrir a biblioteca de poses

Na guia **BoneCraft** na prateleira de ferramentas esquerda, expanda**Review** →**Pose Library**.

---

### Passo 2 — Fazer a pose do avatar

Mova os ossos para a posição que deseja manter: gire os braços, incline a cabeça – qualquer combinação de posições dos ossos é uma pose.

---

### Passo 3 — Salvar a pose

Clique em **Save** e dê um nome à pose (por exemplo "Sinal de paz" ou "Pensando").**Category** arquiva-o em um grupo como "Saudações"; o**Filter** na parte superior mostra uma categoria por vez. Uma miniatura da janela de visualização é capturada com a pose.

---

### Passo 4 — Aplicar uma pose salva

Selecione uma pose e clique em **Apply**.

- **Blend** — aplica a pose com força parcial, para misturar duas poses
- **Mirror** — aplica a pose invertida da esquerda para a direita

**Rename** e**Delete** gerenciam a lista.

---

### Passo 5 — Exportar e importar poses

**Export** salva sua biblioteca de poses em um arquivo `.bfpose` que você pode manter com o projeto ou compartilhar.**Import** carrega poses de um arquivo `.bfpose`.

**O que isso desbloqueia:** Uma biblioteca de poses pessoal que você pode reutilizar em projetos, combinar para chaves de animação ou compartilhar com outros usuários do BoneCraft.

---

## Guia 11: junte dois rigs

> **Tempo:** Cerca de 25 a 40 minutos, dependendo da complexidade
> **Resultado:** Dois esqueletos combinados em um, com todos os pesos mantidos

**Antes de começar - verifique estes:**
- [] O avatar base e o segundo rig (um rig de roupas ou acessórios) estão no mesmo arquivo
- [] Ambos são manipulados e pesados

> Rig merge = absorver um esqueleto em outro, então você acaba com um esqueleto combinado. Útil quando um rig corporal e um rig de cabelo ou roupa devem se tornar um.

---

### Passo 1 — Abrir Mesclagem de Ossos

Na guia **BoneCraft**, expanda a seção**Bone Merge**. Funciona em três etapas; cada um abre quando o anterior é concluído.

---

### Passo 2 — Etapa 1: escopo

Escolha a armadura **Base** (o esqueleto do corpo que fica) e a armadura que se funde a ela (a roupa ou o enfeite de cabelo, que é adicionado à base e depois escondido). Clique em**Analyze**.

BoneCraft compara os dois esqueletos e lista:
- ✓ Combinados — ossos que existem em ambos e se alinham
- \+ Somente fonte — ossos da rig de fusão sem correspondência na base
- − Apenas alvo — ossos de base que o rig de fusão não possui

Depois de ler a lista, clique em **Acknowledge Scope — Proceed to Rename**.

---

### Passo 3 — Etapa 2: renomear

Para cada osso somente de origem, decida o que é:

- Dê a ele o nome do osso base que ele representa e clique em **Apply Rename**
- Clique em **Mark as Unique** se for um osso novo sem equivalente (é adicionado à base como está)

**Normalize Both Armatures** renomeia os ossos padrão (coluna, braços, pernas e assim por diante) que BoneCraft reconhece em ambas as rigs.**Auto-Propose Renames** sugere nomes para o restante da posição de cada osso;**Apply Batch Pattern** renomeia muitos ossos com um padrão.

Quando cada osso somente de origem for resolvido, clique em **Verify Rename — Proceed to Merge**.

---

### Passo 4 — Etapa 3: mesclar

Clique primeiro em **Run Merge Preview**: ele informa o que a mesclagem fará sem alterar nada.

Quando o relatório parecer correto, clique em **Merge Armatures**. BoneCraft faz backup de ambas as armaduras e depois as combina.

**O que você deveria ver:** Uma armadura contendo todos os ossos de ambos os esqueletos, com cada malha pesada sobre ela.

**O que isso desbloqueia:** Um rig único que é mais fácil de exportar e editar. Necessário para qualquer avatar com roupas ou acessórios separados.

---

## Guia 12: resolva problemas de envio

> **Tempo:** Cerca de 5 a 15 minutos, dependendo do problema

**Antes de começar:** Encontre seu problema na lista abaixo e vá para essa seção.

---

### "O envio falhou — ossos não reconhecidos"

Seus ossos têm nomes que VRChat não entende. → [Guia 4: Corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar)

---

### "O avatar está em pose T / não se move comigo no VRChat"

O mapeamento humanóide está ausente ou errado. → [Guia 5: Mapeie seu avatar para o sistema corporal de VRChat](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat)

---

### "A malha se deforma de um jeito estranho / a pele estica errado"

Os pesos ósseos precisam de ajuste. → Consulte Transferência de peso e Espelho de peso em [Ferramentas de plataforma](05-rig-tools.md) ou execute **Smart Automatic Weights** na guia CATS.

---

### "O cabelo atravessa a cabeça"

Os coletores de cabelo estão faltando ou são muito pequenos. → [Guia 6: Adicionar Física ao Cabelo](02-guides-a.md#guia-6-adicione-física-de-cabelo), Etapa 5.

---

### "O avatar tem desempenho Very Poor e outros jogadores o bloqueiam"

→ [Guia 9: Melhore o desempenho do seu avatar](#guia-9-melhore-o-desempenho-do-seu-avatar)

---

### "A sincronia labial não funciona"

Os visemas não estão mapeados corretamente. → [Guia 8: Configurar sincronização labial](#guia-8-configure-a-sincronia-labial)

---

### "O validador de rig mostra erros"

Na guia **BoneCraft**, expanda**Review** →**Rig Validator** e clique em**Run Validation**. Cada resultado nomeia o problema e o osso; siga sua sugestão ou verifique o [Índice de correção rápida](10-reference.md#índice-de-soluções-rápidas).**Export Report** salva os resultados em um arquivo.

---

### "A importação de VRM não funciona"

O complemento VRM pode não estar instalado. → [Guia 2](02-guides-a.md#guia-2-leve-um-avatar-do-vroid-para-o-vrchat), Etapa 1.

---

### "A importação de MMD não funciona"

O complemento mmd_tools pode não estar instalado. → [Guia 3](02-guides-a.md#guia-3-leve-um-avatar-do-mmd-para-o-vrchat), Etapa 1.

---

## Guia 13: prepare seu avatar para o VRChat com o CATS

> **Tempo:** Cerca de 20 a 35 minutos para uma execução completa do pipeline
> **Resultado:** Um avatar limpo e otimizado com sincronização labial, rastreamento ocular e transformações corretas — pronto para upload VRChat

**Antes de começar — leia isto primeiro:**

As ferramentas CATS seguem um pipeline: cada fase deve ser feita em ordem. O status do pipeline da guia CATS mostra uma marca de seleção para cada fase que você realizou (Fix Model, Material Atlas, Visemes, Eye Tracking, Pose To Shape, Apply Transforms) e o Operation Ledger lista cada operação CATS que você executou. Uma ferramenta cuja fase anterior não foi concluída ainda é executada, mas mostra um aviso como "Execute o modelo de correção primeiro para obter melhores resultados".

**Sempre comece com Fix Model. Toda vez. Sem exceção.**

Leia [O gasoduto CATS](04-cats-pipeline.md) antes de continuar, caso ainda não o tenha feito.

**Antes de começar - verifique estes:**
- [] Seu avatar é importado e visível na janela de visualização 3D
- [] A guia CATS está aberta na barra lateral direita (pressione N se a barra lateral estiver oculta)
- [] Seu avatar está selecionado (clique nele na janela de visualização ou no delineador)

---

### Fase 1 — Corrigir Modelo

Fix Model é a base obrigatória para todo o resto em CATS. Execute-o primeiro, mesmo que seu modelo pareça bom: ele remove problemas ocultos que, de outra forma, quebrariam silenciosamente as ferramentas posteriores.

**O que o Fix Model faz** (cada parte pode ser desativada em suas opções):
- Aplica modificadores
- Remove vértices duplicados e geometria solta (triângulos flutuando para longe do corpo)
- Recalcula normais (as direções que decidem qual lado da malha fica voltado para fora)
- Remove grupos de vértices vazios e ossos de peso zero
- Remove restrições e corpos rígidos que VRChat não podem usar

**Etapas:**
1. Na guia **CATS**, expanda**CATS** →**Fix Model**
2. Certifique-se de que a malha do seu avatar esteja selecionada
3. Clique em **Fix Model** e aguarde – para malhas grandes isso leva alguns segundos
4. Verifique se o status do pipeline mostra uma marca de seleção (✓) para Fix Model

**O que você deveria ver:** Seu avatar parece o mesmo ou um pouco mais limpo. O status do pipeline verifica o modelo de correção e o livro razão de operações lista a execução.

> **Se o seu modelo desaparecer ou parecer de dentro para fora após Fix Model:** as normais da malha foram invertidas. Selecione a malha, entre no modo de edição (Tab), selecione tudo (A) e use Mesh > Normals > Flip. Em seguida, execute Fix Model novamente.

---

### Fase 2 — Geração de visemas

Corre atrás: Corrigir Modelo ✓

A seção Visemes cria todos os 15 formatos de boca com sincronização labial VRChat a partir de três formatos básicos que você já possui. Se o seu avatar já possui chaves de formato de visema completas, você pode pular esta fase - mas verifique-as em VRChat Mapeamento de visema (Guia 8).

VRChat precisa de 15 formatos de boca (visemas) para guiar os lábios do seu avatar quando você fala. A maioria dos avatares tem apenas alguns formatos básicos de boca. CATS combina suas formas básicas para fazer o resto.

As três formas básicas:
- **A Shape** - boca bem aberta (formato "ahh")
- **O Shape** - boca arredondada (formato "ohh")
- **CH Shape** - boca estreita e aberta com dentes à mostra (formato "ch" / "sh")

**Etapas:**
1. Na guia **CATS**, expanda**CATS** →**Visemes**
2. Clique em **Auto-Detect** para preencher as três formas ou escolha-as você mesmo (para chaves com nomes como `mouth_open`, `vrc.v_O` ou `mouth_wide`, escolha a correspondência mais próxima)
3. Clique em **Generate Visemes**
4. CATS cria 15 chaves de forma com os nomes de VRChat (`vrc.v_aa`, `vrc.v_O`, `vrc.v_CH` e assim por diante)
5. Verifique se o Status do Pipeline mostra Visemas ✓

**O que você deve ver:** 15 novas chaves de formato na lista Chaves de formato da malha (Propriedades → Dados do objeto → Chaves de formato).

> **Se o seu avatar não tiver nenhuma chave de formato de boca:** crie você mesmo pelo menos A, O e CH (esculpa ou edite-os como chaves de formato) antes que CATS possa gerar o resto. Consulte a entrada do glossário para Shape Key.

---

### Fase 3 — Rastreamento Ocular

Corre atrás: Corrigir Modelo ✓

O Eye Tracking configura os ossos oculares do seu avatar para o rastreamento ocular integrado do VRChat, para que os olhos se movam naturalmente e olhem para outros jogadores.

**O que faz:**
- Encontra os ossos do olho esquerdo e direito
- Nomeia-os conforme VRChat requer (`LeftEye` e `RightEye` )
- Adiciona as restrições de rotação que VRChat precisa para mover os olhos
- Limita a rotação dos olhos a uma faixa natural (para cima, para baixo e para os lados)

Sem o Fix Model primeiro, a detecção de olhos pode travar em vértices duplicados restantes em vez dos olhos reais e colocar as restrições no local errado - os avatares chegam em VRChat com ambos os olhos presos olhando para baixo.

**Etapas:**
1. Na guia **CATS**, expanda**CATS** →**Eye Tracking**
2. Clique em **Auto-Detect** — CATS procura ossos cujos nomes ou posições correspondam aos ossos do olho
3. Verifique os campos **Left Eye** e**Right Eye**; escolha você mesmo os ossos se eles estiverem errados
4. Defina **Up Limit**,**Down Limit** e**Side Limit** se necessário
5. Clique em **Create Eye Tracking**
6. Verifique se o status do pipeline mostra Eye Tracking ✓

**O que você deveria ver:** Ambos os ossos do olho foram renomeados, com restrições de rotação no painel Restrições ósseas.

> **Se CATS não conseguir encontrar os ossos dos olhos:** seu esqueleto pode não ter nenhum. Alguns formatos (especialmente os modelos MMD mais antigos) piscam com chaves de forma em vez de ossos. Pule esta fase: VRChat volta à animação do olho shape-key quando não há ossos oculares.

---

### Fase 4 — Pose para Shape Key

Corre atrás: Corrigir Modelo ✓

Pose to Shape Key transforma a pose atual do seu avatar em uma shape key. Use-o para capturar expressões personalizadas ou poses de descanso para o menu de expressões do VRChat.

Sem Fix Model primeiro, a ordem dos vértices ainda pode conter lacunas de duplicatas removidas, então a chave de forma captura geometria distorcida - chaves de forma que fazem a malha explodir para fora quando acionada em VRChat.

**Etapas:**
1. Posicione seu avatar no modo Pose (selecione a armadura, pressione Ctrl+Tab)
2. Mova os ossos para a expressão ou posição que deseja capturar
3. Retorne ao modo objeto (Ctrl+Tab novamente)
4. Na guia **CATS**, expanda**CATS** →**Pose & Shape Keys**
5. Clique em **Pose to Shape Key** e nomeie a nova chave de forma
6. Verifique se o status do pipeline mostra Pose To Shape ✓

**O que você deveria ver:** Uma nova shape key na lista da malha. Defina seu valor como 1,0 para verificar se mostra a pose.

> **Chave de forma para base:** a ferramenta complementar faz o oposto — ela insere uma chave de forma na forma de repouso neutra da malha. Use-o para travar uma postura de descanso corrigida. Execute-o depois do Fix Model também.

---

### Fase 5 — Aplicar transformações

Corra atrás: cada fase anterior que você precisa

A última fase. Aplicar Transformações congela todas as posições, rotações e escalas na malha e no esqueleto, para que tudo seja lido como valores limpos (posição 0,0,0/rotação 0°,0°,0°/escala 1,0). O SDK VRChat precisa de transformações limpas: a escala não aplicada, em particular, faz com que os avatares apareçam no tamanho errado ou com física que se comporta mal.

A aplicação de transformações antes das fases anteriores incorpora seus problemas na malha para sempre - avatares que parecem corretos em Bforartists, mas aparecem com uma fração de sua altura em VRChat.

**As ferramentas em Transforms e FBT:**
- **Apply All Transforms** — aplica posição, rotação e escala à malha e à armadura juntas
- **Fix FBT** — uma correção de transformação para configurações de Full Body Tracking (move o osso da raiz para o nível do chão)
- **Remove FBT** – remove essa correção novamente

**Etapas:**
1. Confirme se as fases que seu avatar precisa estão marcadas em Status do pipeline (Material Atlas e Pose To Shape são opcionais e Visemas permanecem desmarcados quando você mapeia visemas existentes)
2. Na guia **CATS**, expanda**CATS** →**Transforms & FBT**
3. Clique em **Apply All Transforms**
4. Verifique se o status do pipeline mostra Aplicar transformações ✓
5. Exporte seu avatar (VRChat → Exportar para VRChat, Guia 1 Etapa 9)

**O que você deve ver:** Apply Transforms marcado, após as fases necessárias. Seu avatar está pronto para o VRChat Creator Companion.

---

**O que isso desbloqueia:** Um avatar totalmente processado com geometria limpa, todos os 15 visemas, rastreamento ocular (quando tiver ossos oculares), quaisquer expressões personalizadas que você criou e transformações limpas — tudo o que um upload VRChat precisa para funcionar na primeira vez.

Próximo: [O gasoduto CATS](04-cats-pipeline.md)
