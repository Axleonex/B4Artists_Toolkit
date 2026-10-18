# Primeiros passos

[← Sumário](index.md)

## O que é o BoneCraft?

O BoneCraft é um add-on para o Bforartists que ajuda você a fazer o rig de personagens e acessórios e a preparar avatares 3D para VRChat, VRoid / VRM e MMD. Ele adiciona painéis e botões que automatizam os passos mais trabalhosos: construir um rig, pintar pesos, corrigir nomes de ossos, configurar a sincronia labial e o rastreamento ocular, e exportar.

**O que o BoneCraft não faz:**
- Não modela nem esculpe a forma do corpo do seu avatar
- Não cria texturas nem materiais do zero
- Não envia diretamente para o VRChat (você ainda precisa do VRChat Creator Companion / SDK)

---

## BoneCraft e BoneForge

O BoneCraft só roda no Bforartists (o fork do Blender). Para o Blender padrão existe um add-on separado, o BoneForge, com menos ferramentas. Instale um ou outro, nunca os dois. No Blender padrão, o BoneCraft não carrega: ele mostra um único aviso com um botão para obter o Bforartists.

BoneForge 9.0.0 e versões posteriores são para Blender padrão. BoneCraft é um add-on separado para Bforartists. Ambos têm Auto-Rig Wizard, Quick Rig, Mannequin e ferramentas compartilhadas CATS/Material Atlas. BoneCraft também tem Mechanisms, Control Picker, rigs de controle de produção, detecção de juntas e exportação por perfis. A disposição semelhante não adiciona essas ferramentas ao BoneForge.

## Instalar o BoneCraft

**O que você precisa:**
- Bforartists (o BoneCraft é testado no Bforartists 5.2)
- O arquivo `.zip` do BoneCraft

**Passos:**

1. Abra o Bforartists.
2. Abra **Editar** (Edit) → **Preferências** (Preferences) → **Add-ons**.
3. Clique em **Instalar do disco…** (Install from Disk…) e escolha o arquivo `.zip` do BoneCraft.
4. Marque a caixa ao lado de BoneCraft para ativá-lo.
5. Expanda a entrada do BoneCraft para ver as configurações: **Language** (idioma), **Tabs** (abas), **Shelf Width** (largura), **Show Helpers** (ajudas) e a lista **Ferramentas**.

**O que você deve ver:** as abas BoneCraft e Rig Builder na Tool Shelf da esquerda (pressione **T**) e a aba CATS na barra lateral da direita (pressione **N**).

## Onde fica cada coisa

As abas selecionam grupos de ferramentas. Setup Rigging, Skin, Review, Avatar Tools e Facial são seções expansíveis dentro das abas, não abas separadas. Os caminhos abaixo usam os nomes da interface em inglês; a tradução depende de Language.

| Aba | Local padrão | Seções |
| --- | --- | --- |
| Rig Builder | Tool Shelf esquerda (T) | Auto-Rig Wizard, Quick Rig - premade armatures, Mannequin |
| BoneCraft | Tool Shelf esquerda (T) | Overview, Setup Rigging, Skin, Mechanisms, Review |
| CATS | Barra lateral direita (N) | CATS, Avatar Tools, VRChat Tools, Import / Export |

| Ferramenta | Caminho |
| --- | --- |
| Bone Merge | BoneCraft → Setup Rigging → Bone Merge |
| Delta Mush / Proximity Wrap | BoneCraft → Skin → Delta Mush / Proximity Wrap |
| Viseme Library / Lip Sync | CATS → Avatar Tools → Viseme Library → Lip Sync |
| VRChat Viseme Mapping / Face Tracking | CATS → VRChat Tools → Facial |
| Humanoid / Hair | CATS → Avatar Tools → Set Up Humanoid Bones / Add Hair Physics |
| VRChat export | CATS → Import / Export → Unity / VRChat |
| VRM / MMD / I/O Hub | CATS → Import / Export → VRM / VRoid, MMD / PMX, Game Engine Export |
| Performance / Clothing / Naming | CATS → VRChat Tools → Check Performance / Attach Clothing / VRChat Naming Extras |

Selecione uma armadura para o rig e a biblioteca de visemas; uma malha no Modo Objeto para Delta Mush e Proximity Wrap. Lip Sync requer uma armadura no Modo Pose. Expanda as seções pelo triângulo. Options contém opções; ajuste ferramentas de execução imediata em Ajustar última operação antes de executar outra operação.

Há três fluxos faciais: a geração CATS cria chaves de forma da boca; Viseme Library / Lip Sync salva poses e gera chaves de animação; Facial mapeia chaves existentes para VRChat ou configura rastreamento facial. Os controles derivados de UVToolkit ficam em CATS → Material Atlas → Override Inherited Settings → UV Packing; são o fluxo compartilhado de atlas, não o add-on UVToolkit completo.


**Mover uma aba:** **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Cada aba tem um interruptor e botões Left/Right. A mudança é imediata. Quando oculta, os botões ficam cinza, mas ainda funcionam.

**Editor Properties:** Rig Builder, Mechanisms, CATS, Avatar Tools, VRChat Tools e Import / Export também aparecem na aba Scene com **Scene Properties** ativado em Preferences → Tabs. Começa ligado; **Show** mostra/oculta o conjunto, azul significa visível. Não altera abas da viewport nem Armature data. Com armadura selecionada, ferramentas de armadura BoneCraft também ficam em Armature data, independentemente desses interruptores. Rig Builder, Mechanisms e CATS usam Scene. Para remover uma ferramenta em todos os locais, desligue seu pacote em **Tools**, ou desative o add-on.

**Shelf Width:** Widen Narrow Shelves começa ligado. Amplia uma vez as prateleiras BoneCraft abaixo dos mínimos Left/Right: 240/260 pixels, escala de interface 1×. Se estreitar manualmente depois, a largura escolhida permanece. Desligue para controlar as larguras; os campos ficam inativos.

**Menus e Tool Shelf nativas:** acesso pelos menus do cabeçalho da viewport:

| Local | Ferramentas |
|---|---|
| Add → Armature | Quick Rig, Auto-Rig Wizard, Mannequin for Active Rig |
| Pose → BoneCraft (Pose Mode) | Poses, seletor, coleções, configuração e verificações |
| Weights → BoneCraft (Weight Paint) | Preenchimento, espelho e normalização |
| Object → Mechanisms (Object Mode) | Peças, juntas, ligações, teste |
| Tool Shelf → Pose ou Weights → BoneCraft | Operações comuns de pose ou peso |

Botões Pose/Weights mostram texto em prateleira larga e grade de ícones na estreita. Passe o mouse para ver a dica. São as mesmas ferramentas; a disponibilidade segue os pacotes ativados.

**Ferramentas da viewport:** Place Rig Markers coloca o próximo marcador ao clicar na malha; Build Mechanism inicia junta ou ligação ao clicar numa peça. Veja [Rig Builder](06-rig-builder.md#assistente-auto-rig) e [Mechanisms](07-mechanisms.md) para configurações.

**Executar e depois ajustar:** Quick Rig, Fit Dropped Rig, Weight Mirror, Weight Transfer, Flood to Custom, Ribbon, Spline IK e Delta Mush executam no clique. Ajuste imediatamente em Adjust Last Operation, antes de outra operação. Outros painéis guardam opções num bloco abaixo das ações. Um painel pode permanecer visível explicando a seleção necessária.

**Show Helpers:** desmarque nas preferências para ocultar explicações “o quê/quando” e “How this works”. **Compact Mode** em Avatar Tools controla a mesma configuração.

**Language:** muda os painéis BoneCraft para English, 日本語, 한국어, 中文, Français, Português ou Español.

**Fix Model primeiro, sempre:** comece qualquer trabalho CATS com **Fix Model**. O registro acompanha as etapas e cada ferramenta avisa sobre ordem incorreta. Veja [Pipeline CATS](04-cats-pipeline.md).

**Painel rápido:** **Ctrl+Shift+R** na viewport abre o painel do rig sob o cursor.

---

## Por onde começar?

Escolha a descrição que mais combina com você:

> **"Você tem um arquivo de modelo 3D novinho (FBX, OBJ ou arquivo do Blender) e quer fazer o rig dele para o VRChat do zero."**
> → Vá para o [guia 1: leve seu primeiro avatar para o VRChat](02-guides-a.md#guia-1-leve-seu-primeiro-avatar-para-o-vrchat)

> **"Você criou seu avatar no VRoid Studio e exportou um arquivo VRM."**
> → Vá para o [guia 2: leve um avatar do VRoid para o VRChat](02-guides-a.md#guia-2-leve-um-avatar-do-vroid-para-o-vrchat)

> **"Você tem um modelo do MMD (arquivo PMX) e quer usá-lo no VRChat."**
> → Vá para o [guia 3: leve um avatar do MMD para o VRChat](02-guides-a.md#guia-3-leve-um-avatar-do-mmd-para-o-vrchat)

> **"Você já tem um avatar com rig, mas ele não é enviado porque os ossos têm nomes errados."**
> → Vá para o [guia 4: corrija os nomes dos ossos do seu avatar](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar)

> **"Você tem um avatar com rig e quer deixá-lo totalmente pronto para o VRChat: sincronia labial, rastreamento ocular e malha limpa, tudo de uma vez."**
> → Vá para o [guia 13: prepare seu avatar para o VRChat com o CATS](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats)

> **"Você quer resolver um problema específico."**
> → Vá para o [Índice de soluções rápidas](10-reference.md#índice-de-soluções-rápidas)

Próximo: [Guias 1–7](02-guides-a.md)
