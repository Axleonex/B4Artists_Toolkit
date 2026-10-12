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

| Área | BoneForge (Blender padrão) | BoneCraft (Bforartists) |
| --- | --- | --- |
| Limpeza de avatares CATS, Material Combiner, controles derivados do UVToolkit | Incluído | Incluído |
| Ajudas básicas para avatares (estilo Mixamo) | Incluído | Incluído |
| Construtor de Rig: detecção de articulações, assistente, rig de controle, asset Basic Humanoid | Não incluído | Incluído |
| Controles de animador e o Control Picker | Não incluído | Incluído |
| Mechanisms para acessórios e máquinas | Não incluído | Incluído |
| Redirecionamento avançado e exportação para jogos por perfis | Não incluído | Incluído |

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

O BoneCraft adiciona três abas à viewport 3D:

| Aba | Lado padrão | Seções |
| --- | --- | --- |
| BoneCraft | Tool Shelf da esquerda (pressione T) | Visão Geral, Configurar Rigging, Skin, Mechanisms, Revisão |
| Rig Builder | Tool Shelf da esquerda (pressione T) | Construtor de Rig: Quick Rig, Assistente Auto-Rig, Manequim |
| CATS | Barra lateral da direita (pressione N) | CATS, VRChat, Importar / Exportar |

**Mover uma aba:** abra **Editar** → **Preferências** → **Add-ons** → BoneCraft → **Tabs**. Cada aba tem um interruptor de exibição e dois botões, Left (esquerda) e Right (direita). A mudança vale na hora. Enquanto uma aba está oculta, os botões Left e Right ficam cinza, mas continuam funcionando.

**Sempre no editor de Propriedades:** o Construtor de Rig, Mechanisms, CATS, VRChat e Importar / Exportar também aparecem na aba Cena do editor de Propriedades, seja qual for a seleção. Com uma armadura selecionada, as seções do BoneCraft também aparecem na aba de dados da armadura. Os interruptores de exibição nunca ocultam essas cópias. Para remover uma ferramenta de todos os lugares, desative o pacote dela na lista **Ferramentas**, ou desative o add-on.

**Show Helpers (mostrar ajudas):** o BoneCraft explica suas seções com linhas curtas de "o quê / quando" e notas "How this works" (como funciona). Desmarque **Show Helpers** nas preferências do add-on para ocultá-las. Na seção VRChat, **Modo Compacto** é um atalho para o mesmo interruptor.

**Idioma:** a configuração **Language** (idioma) nas preferências do add-on muda os painéis do próprio BoneCraft para English, 日本語, 한국어, 中文, Français, Português ou Español.

**Corrigir Modelo primeiro, sempre:** na aba CATS, comece sempre com **Corrigir Modelo** antes de qualquer outra ferramenta do CATS. O pipeline do CATS mantém um registro dos passos que você já fez, e cada ferramenta avisa se você a executar fora de ordem. Veja [O pipeline do CATS](04-cats-pipeline.md).

**Painel rápido:** pressione **Ctrl+Shift+R** na viewport 3D para abrir o painel de rig do BoneCraft como uma janela suspensa sob o cursor.

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
