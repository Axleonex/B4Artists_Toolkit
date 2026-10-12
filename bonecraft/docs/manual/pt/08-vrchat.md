# Ferramentas do VRChat

[← Conteúdo](index.md)

## Ferramentas do VRChat

As ferramentas VRChat estão na guia **CATS** na barra lateral direita (pressione**N**), na seção**Avatar Tools**. Suas subseções cobrem ossos humanóides, física do cabelo, mapeamento e exportação de visema. A seção**VRChat Tools** separada abaixo agrupa utilitários de desempenho, roupas e nomenclatura. A mesma seção está na guia**Properties** do editor**Scene** enquanto Preferências → Guias → Propriedades da cena → Mostrar está ativado. Essa opção não oculta a guia da janela de visualização CATS.

---

### Configurar Ossos Humanóides

Mapeia os ossos do seu esqueleto para os slots humanóides do VRChat e verifica o mapeamento.

Consulte [Guia 5: Mapeie seu avatar para o sistema corporal de VRChat](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat).

---

### Adicionar Física de Cabelo

Instala correntes PhysBone em cabelos, orelhas, rabos e acessórios, com colisores.

Consulte [Guia 6: Adicionar Física ao Cabelo](02-guides-a.md#guia-6-adicione-física-de-cabelo).

---

### Anexar Roupa

**Onde encontrar:** Guia CATS → VRChat Ferramentas → Roupas

Funde as roupas no esqueleto do seu avatar e transfere seus pesos.

Consulte [Guia 7: Coloque roupas que se movam com seu corpo](02-guides-a.md#guia-7-anexe-roupas-que-se-movem-com-seu-corpo).

---

### VRChat Naming Extras (extras de nomes do VRChat)

**Onde encontrar:** Guia CATS → VRChat Ferramentas → Nomenclatura

**O que faz:** Detecta o estilo de nomenclatura do seu esqueleto e renomeia os ossos em massa.

Consulte [Guia 4: Corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar).

**Ferramentas de lote:** **Find and Replace**,**Add Prefix**,**Remove Prefix**,**Add Suffix**,**Remove Suffix** e**Regex Replace**

---

### VRChat Viseme Mapping (mapeamento de visemas do VRChat)

**O que faz:** mapeia as chaves de forma da sua malha para os 15 visemas de sincronização labial do VRChat.

Consulte [Guia 8: Configurar sincronização labial](03-guides-b.md#guia-8-configure-a-sincronia-labial). Para criar visemas que seu avatar ainda não possui, consulte [Ferramentas CATS: Visemas](09-cats.md#visemas).

**15 slots de visema de VRChat:** `sil`, `PP`, `FF`, `TH`, `DD`, `kk`, `CH`, `SS`, `nn`, `RR`, `aa`, `E`, `I`, `O`, `U`

---

### Verificar Desempenho

**Onde encontrar:** Guia CATS → VRChat Ferramentas → Desempenho

**O que faz:** Mede a classificação de desempenho VRChat do seu avatar e oferece correções.

Consulte [Guia 9: Melhore o desempenho do seu avatar](03-guides-b.md#guia-9-melhore-o-desempenho-do-seu-avatar).

**Níveis de desempenho (do melhor para o pior):** Excelente → Bom → Médio → Ruim → Muito ruim

**Ferramentas:**
- **Calculate Performance Rank** — a classificação atual, com divisão por polígonos, malhas skinned, slots de material, ossos, PhysBones e contatos
- **Remove Zero-Weight Bones**,**Merge Same-Material Meshes**,**Remove Unused Shape Keys** e**Remove Unused Vertex Groups** — as correções do otimizador (**What-If Mode** mostra o que elas mudariam)
- VRChat Decimation — reduz a contagem de polígonos em uma proporção (**Preview** primeiro, depois**Apply** ), mantendo as chaves de forma seguras

---

### Exportar para VRChat

**O que faz:** exporta seu avatar finalizado como um FBX para o SDK VRChat em Unity. As chaves de forma (formas de mesclagem) são mantidas, a menos que**Remove Shape Keys** esteja ativado.

**Configurações:**
- **Folder** — para onde vai a exportação
- **Avatar** — o nome do arquivo exportado
- **Sidecar** — também grava um arquivo de configurações `.bfvrc` para o importador Unity de BoneCraft
- **Merge Meshes** — une as malhas da cópia de exportação em uma
- **Separate Clothing** — mantém as roupas como malhas separadas
- **Remove Shape Keys** — aplica as chaves de forma à base da cópia de exportação
- **Embed Textures** — empacota as texturas no FBX, para que Unity as encontre
- **Helper Meshes** — inclui malhas ocultas ou auxiliares; deixe desligado para avatares normais

**Botões:** **Export to VRChat (Unity)**,**Generate Sidecar**,**Copy Importer Path** (o caminho do script de importação BoneCraft de Unity ) e**Check / Preserve MToon** para materiais VRM. A seção também repete o status humanóide com**Auto-Map Humanoid**,**Normalize Names** e**Validate**.

---

### Limpeza

A limpeza da malha antes da exportação reside nas ferramentas CATS: **Fix Model**,**Join Meshes** e**Apply All Transforms**. Consulte [Ferramentas CATS](09-cats.md).

---

## Ponte VRM

As ferramentas VRM estão na guia **CATS** →**Import / Export** →**VRM / VRoid**. Eles precisam do complemento VRM; a seção o instala (**Auto-Install Latest from GitHub**,**Install from.zip on Disk…**,**Open Extensions Page** ).

---

### Importação de VRM e VRoid

**O que faz:** Importa avatares `.vrm` (VRoid Studio, Virtual Cast e outros avatares VRM ) com seus materiais, esqueleto e chaves de forma.

- **Import VRM…** — um arquivo `.vrm`
- **Import VRoid (.vroid /.zip)…** — um download do hub VRoid (`.zip` ). Um projeto VRoid Studio (`.vroid` ) mostra um cartão que explica como exportá-lo primeiro para VRM.

---

### VRM Export (exportação VRM)

**O que faz:** Exporta seu personagem manipulado para VRM ou para o formato de um aplicativo de destino.

**Configurações:**
- **Folder** e**File** — para onde vai e seu nome; a extensão segue o alvo
- **Target** — VRM 1.0, VRM 0.x, VRChat FBX, VSeeFace, Warudo ou Resonite
- **Scope** — a armadura ativa ou cada armadura com dados VRM
- Ignorar lint – exportar sem a verificação do alvo; use somente quando você compreender o risco relatado

Clique em **Export…**.

---

### VRM Lint (verificação VRM)

**O que faz:** verifica a armadura em relação ao alvo escolhido antes da exportação: mapeamento humanóide, metadados VRM, visemas do alvo e expectativas do aplicativo alvo.

**Lint Now** executa a verificação sem alterar nada. Os erros bloqueiam a exportação, a menos que você ignore o lint; os avisos explicam o que o aplicativo de destino ainda pode importar, mas funciona pior.

Se o lint disser que ossos humanóides estão faltando, embora existam, clique em **Fix Humanoid Map**: BoneCraft detecta os slots humanóides novamente e salva o mapeamento, sem renomear nenhum osso.

**Também aqui:** **Convert SpringBones → PhysBones** (física do cabelo VRoid para VRChat ) e**Map VRoid Visemes**.

---

## MMD Bridge (ponte MMD)

As ferramentas MMD estão na guia **CATS** →**Import / Export** →**MMD / PMX**. Eles precisam do complemento mmd_tools; a seção o instala (**Auto-Install Latest from GitHub**,**Install from.zip on Disk...** ).

---

### MMD Import (importação MMD)

- **Import PMX / PMD...** — Modelos MMD
- **Import VMD Motion...** — animações MMD
- **Import VPD Pose...** — MMD posa

---

### MMD Export (exportação MMD)

**Configurações:** o**Folder** e, para cada formato, um nome de arquivo e um escopo (o modelo ativo ou cada modelo MMD na cena):**PMX File** e**PMX Scope**,**VMD File** e**VMD Scope**,**VPD File** e**VPD Scope**.

**Botões:** **Export PMX...**,**Export VMD Motion...** e**Export VPD Pose...**

**Também aqui:** **Convert Bone Names -> Unity** e**Convert Physics -> PhysBones**.

---

## Game Export (exportação para jogos)

**O que faz:** Exporta para mecanismos de jogos com perfil validado: Unreal (humanóide ou universal), humanóide Unity, humanóide Godot e FBX ou GLB genérico. Cada correção que o perfil precisa é mostrada e aplicada somente quando você clica nele, nunca silenciosamente.

**Configurações:** o**Profile**, o**Animation** a incluir,**Root Motion**,**Interpolation** e o**T-Pose** usado para exportação (por padrão, uma pose em T para Unity humanóide e VRChat ).

**Botões:**
- **Check for Export** — verifica a rig em relação ao perfil e lista as descobertas
- **Apply Transforms (Fix)** – uma das correções explícitas que a verificação pode oferecer
- **Export (Profile)** — exporta com o perfil

**Onde encontrar:** Guia**CATS** →**Import / Export** →**Game Export**

---

## Quadro de Tarefas

**O que faz:** Um resumo da rig atual: uma pontuação de saúde, ganhos rápidos e uma lista de tarefas que BoneCraft encontrou (ossos humanóides ausentes, nomes não resolvidos, visemas ausentes, avisos do validador da rig e assim por diante), agrupados por categoria.**Open Health Check** abre os detalhes;**Refresh Task Board** verifica novamente.

**Onde encontrar:** Guia**BoneCraft** →**Overview** →**Task Board**

---

### Inspetor de Ossos

**O que ele faz:** Mostra o osso selecionado em detalhes — seu nome, pai, restrições, propriedades personalizadas e drivers — e permite editar propriedades simples sem entrar no Modo de Edição.

**Onde encontrar:** Guia**BoneCraft** →**Review** →**Bone Inspector**

Próximo: [Ferramentas CATS](09-cats.md)
