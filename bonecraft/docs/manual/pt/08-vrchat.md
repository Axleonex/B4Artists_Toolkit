# Ferramentas do VRChat

[← Sumário](index.md)

## Ferramentas do VRChat

As abas selecionam grupos de ferramentas. Setup Rigging, Skin, Review, Avatar Tools e Facial são seções expansíveis dentro das abas, não abas separadas. Os caminhos abaixo usam os nomes da interface em inglês; a tradução depende de Language.

| Ferramenta | Caminho |
| --- | --- |
| Humanoid / Hair / Export | CATS → Avatar Tools |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Performance / Clothing / Naming | CATS → VRChat Tools |

Preferências: Edit → Preferences → Add-ons → BoneCraft → Tabs controla as abas. Scene Properties controla separadamente os painéis Rig Builder e CATS em Properties → Scene. Show Helpers oculta explicações; Language altera os rótulos; Tools ativa os pacotes. Ctrl+Shift+R abre o painel rápido.

---

### Configurar Ossos Humanóides

Mapeia os ossos do seu esqueleto para os slots humanoides do VRChat e verifica o mapeamento.

Veja o [guia 5: mapeie seu avatar para o sistema corporal do VRChat](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat).

---

### Adicionar Física de Cabelo

Configura cadeias PhysBone em cabelo, orelhas, caudas e acessórios, com colisores.

Veja o [guia 6: adicione física de cabelo](02-guides-a.md#guia-6-adicione-física-de-cabelo).

---

### Anexar Roupa

Mescla a roupa no esqueleto do seu avatar e transfere os pesos dela.

Veja o [guia 7: anexe roupas que se movem com seu corpo](02-guides-a.md#guia-7-anexe-roupas-que-se-movem-com-seu-corpo).

---

### VRChat Naming Extras (extras de nomes do VRChat)

**O que faz:** detecta o estilo de nomes do seu esqueleto e renomeia ossos em massa.

Veja o [guia 4: corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar).

**Ferramentas em lote:** **Localizar e Substituir**, **Adicionar Prefixo**, **Remover Prefixo**, **Adicionar Sufixo**, **Remover Sufixo** e **Substituição por Regex**

---

### VRChat Viseme Mapping (mapeamento de visemas do VRChat)

**O que faz:** mapeia os shape keys da sua malha para os 15 visemas de sincronia labial do VRChat.

Veja o [guia 8: configure a sincronia labial](03-guides-b.md#guia-8-configure-a-sincronia-labial). Para criar visemas que seu avatar ainda não tem, veja [Ferramentas do CATS: Visemas](09-cats.md#visemas).

**Os 15 slots de visemas do VRChat:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Verificar Desempenho

**O que faz:** mede a classificação de desempenho do seu avatar no VRChat e oferece correções.

Veja o [guia 9: melhore o desempenho do seu avatar](03-guides-b.md#guia-9-melhore-o-desempenho-do-seu-avatar).

**Níveis de desempenho (do melhor ao pior):** Excellent → Good → Medium → Poor → Very Poor

**Ferramentas:**
- **Calculate Performance Rank** (calcular classificação de desempenho) — a classificação atual, detalhada por polígonos, malhas com skin, slots de material, ossos, PhysBones e contatos
- **Remover Ossos de Peso Zero**, **Mesclar Malhas do Mesmo Material**, **Remover Shape Keys Não Utilizados** e **Remover Grupos de Vértices Não Utilizados** — as correções do otimizador (**Modo Hipotético** mostra o que elas mudariam)
- Decimação VRChat — reduz o número de polígonos por uma proporção (**Pré-visualizar** primeiro, depois **Aplicar**), protegendo os shape keys

---

### Exportar para VRChat

**O que faz:** exporta seu avatar pronto como FBX para o SDK do VRChat no Unity. Os shape keys (blend shapes) são mantidos, a menos que **Remove Shape Keys** esteja ativado.

**Configurações:**
- **Folder** (pasta) — para onde vai a exportação
- **Avatar** — o nome do arquivo exportado
- **Sidecar** — grava também um arquivo de configurações `.bfvrc` para o importador do Unity do BoneCraft
- **Merge Meshes** (mesclar malhas) — une as malhas da cópia de exportação em uma
- **Separate Clothing** (roupa separada) — mantém a roupa como malhas separadas
- **Remove Shape Keys** (remover shape keys) — aplica os shape keys à base da cópia de exportação
- **Embed Textures** (incorporar texturas) — empacota as texturas no FBX, para que o Unity as encontre
- **Helper Meshes** (malhas auxiliares) — inclui malhas ocultas ou auxiliares; deixe desativado para avatares normais

**Botões:** **Exportar para VRChat (Unity)**, **Gerar Sidecar**, **Copiar Caminho do Importador** (o caminho do script de importação do Unity do BoneCraft) e **Verificar / Preservar MToon** para materiais VRM. A seção também repete o status humanoide com **Auto-Map Humanoid** (mapear humanoide automaticamente), **Normalize Names** (normalizar nomes) e **Validar**.

---

### Limpeza

A limpeza da malha antes da exportação fica nas ferramentas do CATS: **Corrigir Modelo**, **Unir Malhas** e **Aplicar Todos os Transformes**. Veja [Ferramentas do CATS](09-cats.md).

---

## Ponte VRM

As ferramentas de VRM ficam na aba **CATS** → **Importar / Exportar** → **VRM / VRoid**. Elas precisam do add-on VRM; a seção o instala (**Instalar Automaticamente do GitHub**, **Instalar do .zip no Disco…**, **Abrir Página de Extensões**).

---

### Importação de VRM e VRoid

**O que faz:** importa avatares `.vrm` (VRoid Studio, Virtual Cast e outros avatares VRM) com seus materiais, esqueleto e shape keys.

- **Importar VRM…** — um arquivo `.vrm`
- **Import VRoid (.vroid / .zip)…** (importar VRoid) — um download do VRoid Hub (`.zip`). Um projeto do VRoid Studio (`.vroid`) mostra um cartão que explica como exportá-lo antes para VRM.

---

### VRM Export (exportação VRM)

**O que faz:** exporta seu personagem com rig para VRM, ou para o formato de um aplicativo de destino.

**Configurações:**
- **Folder** e **File** (arquivo) — para onde vai e o nome; a extensão acompanha o destino
- **Alvo** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo ou Resonite
- **Scope** (escopo) — a armadura ativa, ou cada armadura com dados VRM
- Skip lint (pular verificação) — exportar sem a verificação do destino; use só se você entende o risco informado

Clique em **Exportar…**.

---

### VRM Lint (verificação VRM)

**O que faz:** verifica a armadura em relação ao destino escolhido antes da exportação: mapeamento humanoide, metadados VRM, os visemas do destino e o que o aplicativo de destino espera.

**Verificar Agora** executa a verificação sem mudar nada. Os erros bloqueiam a exportação, a menos que você pule a verificação; os avisos explicam o que o aplicativo de destino ainda pode importar, mas com funcionamento pior.

Se a verificação disser que faltam ossos humanoides embora eles existam, clique em **Fix Humanoid Map** (corrigir mapa humanoide): o BoneCraft detecta de novo os slots humanoides e salva o mapeamento, sem renomear nenhum osso.

**Também aqui:** **Converter SpringBones → PhysBones** (física de cabelo do VRoid para o VRChat) e **Mapear Visemas VRoid**.

---

## MMD Bridge (ponte MMD)

As ferramentas de MMD ficam na aba **CATS** → **Importar / Exportar** → **MMD / PMX**. Elas precisam do add-on mmd_tools; a seção o instala (**Instalar Automaticamente do GitHub**, **Install from .zip on Disk...** (instalar de um .zip no disco)).

---

### MMD Import (importação MMD)

- **Import PMX / PMD...** (importar PMX / PMD) — modelos MMD
- **Import VMD Motion...** (importar movimento VMD) — animações MMD
- **Import VPD Pose...** (importar pose VPD) — poses MMD

---

### MMD Export (exportação MMD)

**Configurações:** a **Folder** e, para cada formato, um nome de arquivo e um escopo (o modelo ativo, ou cada modelo MMD da cena): **PMX File** e **PMX Scope**, **VMD File** e **VMD Scope**, **VPD File** e **VPD Scope**.

**Botões:** **Export PMX...** (exportar PMX), **Export VMD Motion...** (exportar movimento VMD) e **Export VPD Pose...** (exportar pose VPD)

**Também aqui:** **Convert Bone Names -> Unity** (converter nomes de ossos para o Unity) e **Convert Physics -> PhysBones** (converter física em PhysBones).

---

## Game Engine Export (exportação para jogos)

**O que faz:** exporta para engines de jogo com um perfil validado: Unreal (humanoide ou universal), humanoide do Unity, humanoide do Godot, e FBX ou GLB genéricos. Cada correção de que o perfil precisa é mostrada e só é aplicada quando você clica nela, nunca em silêncio.

**Configurações:** o **Profile** (perfil), a **Animation** (animação) a incluir, **Root Motion** (movimento da raiz), **Interpolation** (interpolação) e a **T-Pose** usada na exportação (por padrão uma pose T para o humanoide do Unity e o VRChat).

**Botões:**
- **Check for Export** (verificar para exportação) — confere o rig em relação ao perfil e lista o que encontrou
- **Apply Transforms (Fix)** (aplicar transformações (correção)) — uma das correções explícitas que a verificação pode oferecer
- **Export (Profile)** (exportar (perfil)) — exporta com o perfil

**Onde fica:** aba **CATS** → **Importar / Exportar** → **Game Engine Export**

---

## Quadro de Tarefas

**O que faz:** um resumo do rig atual: uma pontuação de saúde, ganhos rápidos e uma lista das tarefas que o BoneCraft encontrou (ossos humanoides faltando, nomes não resolvidos, visemas faltando, avisos do validador de rig etc.), agrupadas por categoria. **Abrir verificação de saúde** abre os detalhes; **Atualizar Quadro de Tarefas** verifica de novo.

**Onde fica:** aba **BoneCraft** → **Visão Geral** → **Quadro de Tarefas**

---

### Inspetor de Ossos

**O que faz:** mostra em detalhes o osso selecionado (nome, pai, restrições, propriedades personalizadas e drivers) e permite editar propriedades simples sem entrar no Modo Edição.

**Onde fica:** aba **BoneCraft** → **Revisão** → **Inspetor de Ossos**

Próximo: [Ferramentas do CATS](09-cats.md)
