# Primeiros passos

[← Conteúdo](index.md)

## O que é o BoneCraft?

BoneCraft é um complemento para Bforartists que ajuda você a equipar personagens e acessórios e preparar avatares 3D para VRChat, VRoid / VRM e MMD. Ele adiciona painéis e botões que automatizam as etapas mais tediosas: construir um rig, pintar pesos, corrigir nomes de ossos, configurar sincronização labial e rastreamento ocular e exportar.

**O que BoneCraft não pode fazer:**
- Não pode modelar ou esculpir o formato do corpo do seu avatar
- Não pode criar texturas ou materiais do zero
- Ele não pode fazer upload diretamente para VRChat (você ainda precisa do VRChat Creator Companion/SDK)

---

## BoneCraft e BoneForge

BoneCraft é executado apenas em Bforartists (a bifurcação Blender ). Para o Blender padrão, há um complemento separado, BoneForge, com um conjunto menor de ferramentas. Instale um ou outro, nunca ambos. No padrão Blender, BoneCraft não carrega: mostra um aviso com um botão para obter Bforartists.

|Área|BoneForge (padrão Blender )|BoneCraft (Bforartists )|
| --- | --- | --- |
|Limpeza de avatar CATS, Combinador de materiais, controles derivados de UVToolkit|Incluído|Incluído|
|Ajudantes básicos de avatar (estilo Mixamo)|Incluído|Incluído|
|Rig Builder: detecção de juntas, assistente, rig de controle, recurso Humanóide Básico|Não incluído|Incluído|
|Controles do Animator e o Seletor de Controle|Não incluído|Incluído|
|Mecanismos para adereços e máquinas|Não incluído|Incluído|
|Redirecionamento avançado e exportação de jogos baseada em perfil|Não incluído|Incluído|

## Instalar o BoneCraft

**O que você precisa:**
- Bforartists (BoneCraft é testado em Bforartists 5.2)
- O arquivo BoneCraft `.zip`

**Etapas:**

1. Abra Bforartists.
2. Abra **Edit** →**Preferences** →**Add-ons**.
3. Clique em **Install from Disk…** e selecione o arquivo BoneCraft `.zip`.
4. Marque a caixa de seleção ao lado de BoneCraft para habilitá-lo.
5. Expanda a entrada BoneCraft para ver suas configurações: **Language**,**Tabs**,**Shelf Width**,**Show Helpers** e a lista**Tools**.

**Você deverá ver:** as guias BoneCraft e Rig Builder na prateleira de ferramentas esquerda (pressione**T**) e a guia CATS na barra lateral direita (pressione**N**).

## Onde fica cada coisa

BoneCraft adiciona três guias à viewport 3D:

|Guia|Lado padrão|Seções|
| --- | --- | --- |
|BoneCraft |Prateleira de ferramentas esquerda (pressione T)|Visão geral, configuração de rigging, skin, mecanismos, revisão|
|Construtor de rig|Prateleira de ferramentas esquerda (pressione T)|Construtor de Rig: Assistente de Auto-Rig, Quick Rig, Manequim|
|CATS |Barra lateral direita (pressione N)|CATS, Ferramentas de Avatar, Ferramentas VRChat, Importação/Exportação|

**Mover uma guia:** abra**Edit** →**Preferences** →**Add-ons** → BoneCraft →**Tabs**. Cada guia possui um botão de exibição e dois botões, Esquerdo e Direito. Uma mudança se aplica imediatamente. Enquanto uma guia está oculta, os botões Esquerdo e Direito ficam cinza, mas ainda funcionam.

**Editor de propriedades:** Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools e Import/Export também são mostrados na guia Scene do editor Properties enquanto**Scene Properties** está ativado em Preferences → Tabs. Esta opção é ativada. Clique no botão**Show** para ocultar ou mostrar todas essas seções; azul significa que eles são mostrados. Isso não altera as guias da janela de visualização ou a guia Dados da armadura. Com uma armadura selecionada, as ferramentas de armadura do BoneCraft também aparecem na guia Dados da armadura, independentemente dessas opções de visibilidade. As seções Rig Builder, Mechanisms e CATS usam a guia Scene. Para remover uma ferramenta de qualquer lugar, desative seu pacote na lista**Tools** ou desative o complemento.

**Largura da prateleira:** Ampliar prateleiras estreitas começa. Ele amplia as prateleiras contendo as guias BoneCraft uma vez se estiverem abaixo do mínimo Esquerdo ou Direito: 240 e 260 pixels por padrão, na escala de 1× da UI. Uma prateleira que você arrasta para mais estreita depois permanece na largura escolhida. Desligue o interruptor para gerenciar as larguras você mesmo; seus campos de largura ficam inativos.

**Menus e guias internas da prateleira de ferramentas:** na versão 9.1, você também pode acessar ferramentas nos menus de cabeçalho da janela de visualização 3D:

|Localização|Ferramentas|
| --- | --- |
|Adicionar → Armadura|Quick Rig, Auto-Rig Wizard, Manequim para Active Rig|
|Pose → BoneCraft (modo de pose)|Ferramentas de pose, selecionador, coleções de ossos, configuração e verificações da rig|
|Pesos → BoneCraft (modo Pintura de peso)|Preencher, espelhar e normalizar pesos|
|Objeto → Mecanismos (Modo Objeto)|Adicione peças, juntas e links; movimento de teste|
|Prateleira de ferramentas → Posição ou Pesos → BoneCraft |Botões para operações comuns de pose ou peso|

Os botões da prateleira Pose e Pesos mostram texto quando a prateleira é larga e se tornam uma grade de ícones quando ela é estreita. Passe o mouse sobre um ícone para ler sua dica de ferramenta. Esses pontos de acesso usam as mesmas ferramentas das próprias guias do BoneCraft; sua disponibilidade segue os pacotes de ferramentas habilitados.

**Ferramentas de viewport:** Place Rig Markers coloca o próximo marcador do Auto-Rig Wizard quando você clica na malha; O Build Mechanism inicia uma junta ou link guiado quando você clica em uma peça. Consulte [Construtor de plataforma](06-rig-builder.md#assistente-auto-rig) e [Mecanismos](07-mechanisms.md#articulações-e-ligações-um-exemplo-de-cada) para obter suas configurações e controles.

**Execute primeiro, ajuste depois:** ferramentas como Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK e Delta Mush são executadas quando clicadas. Imediatamente depois, use o painel Ajustar última operação na viewport para alterar suas opções. Ajuste antes de executar outra operação. Outros painéis colocam configurações opcionais em uma dobra abaixo dos botões de ação; expanda-o quando precisar dessas configurações. Um painel que precisa de uma seleção diferente pode permanecer visível e explicar o que selecionar.

**Mostrar ajudantes:** BoneCraft explica suas seções com linhas curtas "o que/quando" e notas "Como isso funciona". Desmarque**Show Helpers** nas preferências do complemento para ocultá-los. Na seção Ferramentas de Avatar,**Compact Mode** é um atalho para o mesmo switch.

**Idioma:** a configuração**Language** nas preferências do complemento altera os próprios painéis do BoneCraft para inglês, 日本語, 한국어, 中文, Français, Português ou Español.

**Corrija o modelo primeiro, sempre:** na guia CATS, sempre comece com**Fix Model** antes de qualquer outra ferramenta CATS. O pipeline CATS usa um livro-razão para rastrear quais etapas você executou e cada ferramenta avisa se você executá-lo fora de ordem. Consulte [O gasoduto CATS](04-cats-pipeline.md).

**Painel rápido:** pressione**Ctrl+Shift+R** na janela de visualização 3D para abrir o painel de rig do BoneCraft como um pop-up sob o cursor.

---

## Por onde começar?

Escolha a descrição que melhor se adapta a você:

> **"Você é uma pessoa que possui um novo arquivo de modelo 3D (arquivo FBX, OBJ ou Blender ) e deseja prepará-lo para VRChat do zero."**
> → Vá para [Guia 1: Obtenha seu primeiro avatar em VRChat](02-guides-a.md#guia-1-leve-seu-primeiro-avatar-para-o-vrchat)

> **"Você é uma pessoa que criou seu avatar no VRoid Studio e exportou um arquivo VRM."**
> → Vá para [Guia 2: Traga um avatar VRoid para VRChat](02-guides-a.md#guia-2-leve-um-avatar-do-vroid-para-o-vrchat)

> **"Você é uma pessoa que possui um modelo MMD (arquivo PMX ) e deseja usá-lo em VRChat."**
> → Vá para [Guia 3: Traga um Avatar MMD para VRChat](02-guides-a.md#guia-3-leve-um-avatar-do-mmd-para-o-vrchat)

> **"Você é uma pessoa que já tem um avatar fraudado, mas ele não carrega porque os ossos têm nomes errados."**
> → Vá para [Guia 4: Corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar)

> **"Você é uma pessoa que tem um avatar manipulado e deseja deixá-lo totalmente pronto para VRChat - sincronização labial, rastreamento ocular, malha limpa, tudo de uma vez."**
> → Vá para [Guia 13: Prepare seu avatar VRChat com CATS](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats)

> **"Você é uma pessoa que deseja resolver um problema específico."**
> → Vá para [Índice de correção rápida](10-reference.md#índice-de-soluções-rápidas)

Próximo: [Guias 1–7](02-guides-a.md)
