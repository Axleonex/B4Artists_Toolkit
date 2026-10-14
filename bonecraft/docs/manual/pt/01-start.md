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
5. Expanda a entrada do BoneCraft para ver as configurações: **Tabs** (abas), **Show Helpers** (mostrar ajudas), **Language** (idioma) e a lista **Ferramentas**.

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

Preferências: Edit → Preferences → Add-ons → BoneCraft → Tabs controla as abas. Scene Properties controla separadamente os painéis Rig Builder, Mechanisms e CATS em Properties → Scene. Show Helpers oculta explicações; Language altera os rótulos; Tools ativa os pacotes. Ctrl+Shift+R abre o painel rápido.

BoneCraft move abas com Left / Right em Preferences → Tabs. Scene Properties → Show começa ativado. Também há painéis de dados da armadura e botões nas Tool Shelf nativas Pose / Weights. Esses acessos são específicos de Bforartists.

Há três fluxos faciais: a geração CATS cria chaves de forma da boca; Viseme Library / Lip Sync salva poses e gera chaves de animação; Facial mapeia chaves existentes para VRChat ou configura rastreamento facial. Os controles derivados de UVToolkit ficam em CATS → Material Atlas → Override Inherited Settings → UV Packing; são o fluxo compartilhado de atlas, não o add-on UVToolkit completo.

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
