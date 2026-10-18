# Guias 1–7

[← Sumário](index.md)

## Guia 1: leve seu primeiro avatar para o VRChat

> **Tempo:** cerca de 45–60 minutos para uma primeira passagem completa
> **Resultado:** um avatar com rig, pronto para o VRChat, exportado para o SDK do VRChat

**Antes de começar, verifique:**
- [ ] Seu modelo 3D está importado no Bforartists (Arquivo > Importar, escolha o formato)
- [ ] O modelo está em pose T (braços estendidos para os lados, corpo ereto), ou quase
- [ ] O modelo não tem geometria visivelmente quebrada (nada de triângulos soltos flutuando)
- [ ] Você vê seu modelo na viewport 3D como uma forma cinza sólida

---

### Passo 1 — Abrir o Construtor de Rig

Abra Rig Builder na Tool Shelf esquerda (T). Ordem: Auto-Rig Wizard, Quick Rig, Mannequin. A cópia em Properties → Scene aparece quando Preferences → Tabs → Scene Properties → Show está ativado.

Expanda **Assistente Auto-Rig** e clique em **Iniciar Auto-Rig**.

---

### Passo 2 — Selecionar sua malha

O assistente lista as malhas da cena. Clique na malha do seu avatar nessa lista e depois em **Próximo**.

**O que você deve ver:** uma linha "Selected:" com o nome da sua malha e, em seguida, o passo do tipo de rig.

---

### Passo 3 — Escolher o tipo de rig

Clique em **Body + Face** (corpo e rosto) para um avatar cujo rosto você quer animar (piscadas, expressões, sincronia labial), ou em **Body Only** (só corpo) para um corpo sem controles faciais. Nas opções de geração, **Cinemática** escolhe IK/FK, só IK ou só FK. Clique em **Próximo**.

---

### Passo 4 — Posicionar os marcadores do corpo

Este é o passo mais importante. Os marcadores são pontos que mostram ao BoneCraft onde fica cada articulação principal: a pelve, a coluna, o pescoço e a cabeça, os ombros, os braços, as mãos, as pernas e os pés. O BoneCraft calcula os ossos a partir deles.

**O jeito rápido:** no quadro Smart Detection (detecção inteligente), clique em **Detect Markers** (detectar marcadores). O BoneCraft percorre os membros da sua malha e posiciona cada marcador, cada um com um grau de confiança. Clique em **Accept High** (aceitar confiança alta) para manter os seguros e em **Reset Low** (redefinir confiança baixa) para apagar os duvidosos e posicioná-los você mesmo. **Adivinhar marcadores da malha** é uma estimativa mais simples a partir das proporções da malha.

**À mão:** cada marcador tem uma linha de botões com ícone.
1. Clique em **Place Marker** (posicionar marcador; o ícone de seta) na linha do marcador e depois no ponto certo do seu avatar.
2. Clique em **Confirm Marker** (confirmar marcador; a marca de verificação) quando ele estiver no lugar certo. **Reset Marker** (redefinir marcador; a seta circular) apaga um marcador posicionado para você posicioná-lo de novo.

**Simetria:** **Toggle Symmetry** (alternar simetria; o primeiro ícone na linha de um marcador esquerdo ou direito) posiciona o marcador do outro lado sempre que você posiciona este. **Mirror L to R** (espelhar da esquerda para a direita) e **Mirror R to L** (espelhar da direita para a esquerda) copiam cada marcador confirmado para o outro lado.

Quando todos os marcadores estiverem posicionados, clique em **Confirmar todos colocados** e depois em **Próximo**.

---

### Passo 5 — Posicionar os marcadores dos dedos

Em Detalhe dos Dedos, escolha quantos dedos construir: "5 — Full Human Hand" para uma mão padrão, ou menos (até "0 — No Fingers"). Clique em **Adivinhar marcadores de dedos**. O BoneCraft encontra cada dedo a partir da forma da mão e o percorre do nó do dedo até a ponta. Ajuste os marcadores fora do lugar e clique em **Próximo**.

---

### Passo 6 — Posicionar os marcadores do rosto (só Body + Face)

Clique em **Adivinhar marcadores faciais** e ajuste conforme necessário os olhos, as pálpebras, as sobrancelhas, os cantos da boca e a mandíbula. Os marcadores dos olhos ficam onde você os coloca. Clique em **Próximo**.

---

### Passo 7 — Revisar e gerar

O passo de revisão lista os avisos e as opções de geração. Clique em **Gerar rig**.

**O que você deve ver:** um esqueleto (ossos laranja) dentro do seu avatar, com membros IK/FK, ossos dos dedos e, em um rig Body + Face, um rig facial, e a pele do avatar presa a ele, de modo que ela se deforma quando os ossos se movem. O último passo oferece **Construir Rig de Controle** para as opções da revisão que Gerar rig não aplica, e **Fechar assistente**; [Construtor de Rig](06-rig-builder.md) descreve os dois.

> **Pesos de pele** = números que decidem quais ossos movem quais partes da malha do seu avatar. O BoneCraft os define automaticamente; você pode refiná-los com as ferramentas de pesos (veja [Ferramentas de rig](05-rig-tools.md)).

---

### Passo 8 — Mapear para os ossos humanoides do VRChat

Abra a aba **CATS** na barra lateral da direita (pressione **N**), expanda **Avatar Tools** e depois **Configurar Ossos Humanóides**. Clique em **Mapear Tudo Automaticamente**: o BoneCraft conecta seus ossos aos slots do corpo que o VRChat usa para mover um avatar junto com você. Clique em **Normalize Names** (normalizar nomes) para dar aos ossos mapeados os nomes que o VRChat espera e depois em **Validar**.

**O que você deve ver:** os slots obrigatórios (Hips, Spine, Head, LeftUpperArm etc.) mostram cada um um osso. O guia 5 explica os slots.

---

### Passo 9 — Exportar para o VRChat

Na aba **CATS**, expanda **Import / Export** → **Unity / VRChat**. Defina a **Folder** (pasta) e o nome do **Avatar** e clique em **Exportar para VRChat (Unity)**.

**O que você deve ver:** o avatar exportado na pasta escolhida, pronto para o VRChat Creator Companion e o SDK do VRChat no Unity.

---

**O que isso libera:** agora você tem um avatar de VRChat com rig. A partir daqui, você pode adicionar física de cabelo (guia 6), anexar roupas (guia 7), configurar a sincronia labial (guia 8) e verificar o desempenho (guia 9). Para uma limpeza e configuração de VRChat completas com as ferramentas do CATS, veja o [guia 13](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats).

---

## Guia 2: leve um avatar do VRoid para o VRChat

> **Tempo:** cerca de 15–25 minutos
> **Resultado:** seu avatar do VRoid pronto para exportar para o VRChat

**Antes de começar, verifique:**
- [ ] Você exportou seu avatar do VRoid Studio como arquivo `.vrm`, ou o baixou do VRoid Hub como `.zip`
- [ ] O BoneCraft está instalado e ativado

---

### Passo 1 — Instalar o add-on VRM

O BoneCraft usa o add-on VRM para ler arquivos `.vrm`. Na aba **CATS**, expanda **Importar / Exportar** → **VRM / VRoid**. Se aparecer que o add-on não está instalado, clique em **Instalar Automaticamente do GitHub**. Sem conexão com a internet, baixe o add-on você mesmo e use **Instalar do .zip no Disco…**; **Abrir Página de Extensões** abre a página de download dele.

---

### Passo 2 — Importar seu avatar

Na mesma seção **VRM / VRoid**, clique em **Importar VRM…** e escolha seu arquivo `.vrm`. Para um download do VRoid, clique em **Import VRoid (.vroid / .zip)…** (importar VRoid) e escolha o `.zip`.

Se você escolher um arquivo de projeto do VRoid Studio (`.vroid`), o BoneCraft mostra em vez disso um cartão "VRoid Studio Project": um projeto ainda não é um avatar. Exporte-o para VRM no VRoid Studio e depois importe esse arquivo.

**O que você deve ver:** seu personagem do VRoid na viewport, com o esqueleto no lugar.

---

### Passo 3 — Mapear para os ossos humanoides do VRChat

Na aba **CATS** → **Avatar Tools** → **Configurar Ossos Humanóides**, clique em **Mapear Tudo Automaticamente**. Os esqueletos do VRoid seguem um layout padrão, então isso normalmente preenche todos os slots. Se um slot estiver errado, **Fix Humanoid Map** (corrigir mapa humanoide) na seção **VRM / VRoid** (em Lint) corrige as confusões de nomes comuns do VRoid.

---

### Passo 4 — Corrigir os nomes dos ossos

Clique em **Normalize Names** em **Configurar Ossos Humanóides**. O VRoid tem seus próprios nomes de ossos; isso dá aos ossos mapeados os nomes que o VRChat espera.

---

### Passo 5 — Configurar os visemas (sincronia labial)

Os avatares do VRoid já têm as formas de boca para a sincronia labial. Na seção **VRM / VRoid**, clique em **Mapear Visemas VRoid**. O BoneCraft associa os shape keys do VRoid às formas de sincronia labial do VRChat.

---

### Passo 6 — Física de cabelo (opcional)

O cabelo do VRoid usa SpringBones. **Converter SpringBones → PhysBones** na seção **VRM / VRoid** os transforma em PhysBones do VRChat. O guia 6 trata da física de cabelo com mais detalhes.

---

### Passo 7 — Exportar

Exporte como no guia 1, passo 9.

**O que isso libera:** seu avatar do VRoid está pronto para o VRChat Creator Companion. Você também pode verificar o desempenho (guia 9) antes de enviar.

---

## Guia 3: leve um avatar do MMD para o VRChat

> **Tempo:** cerca de 20–30 minutos
> **Resultado:** seu modelo `.pmx` do MMD pronto para o VRChat

**Antes de começar, verifique:**
- [ ] Você tem um arquivo de modelo MMD `.pmx` ou `.pmd`
- [ ] O BoneCraft está instalado

---

### Passo 1 — Instalar o mmd_tools

O BoneCraft usa o add-on mmd_tools para ler arquivos MMD. Na aba **CATS**, expanda **Importar / Exportar** → **MMD / PMX**. Se aparecer que o mmd_tools não está instalado, clique em **Instalar Automaticamente do GitHub** (ou em **Install from .zip on Disk...** (instalar de um .zip no disco) com uma cópia baixada).

---

### Passo 2 — Importar seu arquivo PMX

Na seção **MMD / PMX**, clique em **Import PMX / PMD...** (importar PMX / PMD) e escolha seu modelo.

**O que você deve ver:** seu personagem do MMD na viewport, com nomes de ossos em japonês.

---

### Passo 3 — Corrigir os nomes dos ossos

O VRChat não consegue ler os nomes de ossos em japonês do MMD. Na seção **MMD / PMX**, clique em **Convert Bone Names -> Unity** (converter nomes de ossos para o Unity). Para nomes em outro idioma, use a aba **CATS** → **CATS** → **Traduzir Nomes de Ossos**: escolha o **Idioma** e execute.

---

### Passo 4 — Limpar o modelo

Os modelos do MMD costumam ter geometria a mais e muitas peças separadas. Na aba **CATS** → **CATS**, execute primeiro **Corrigir Modelo** e depois **Unir Malhas** para combinar as partes do corpo em uma só malha (recomendado para o VRChat). O [guia 13](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats) percorre todo o pipeline do CATS em ordem.

---

### Passo 5 — Mapear para os ossos humanoides do VRChat

Na aba **CATS** → **Avatar Tools** → **Configurar Ossos Humanóides**, clique em **Mapear Tudo Automaticamente**. Os esqueletos do MMD são parecidos com os do VRChat, então a maioria dos slots se preenche sozinha. Para um slot vazio, clique no botão dele e escolha o osso.

---

### Passo 6 — Física e exportação

**Convert Physics -> PhysBones** (converter física em PhysBones) na seção **MMD / PMX** transforma a física de corpos rígidos do cabelo e da saia do MMD em PhysBones do VRChat. Depois exporte como no guia 1, passo 9.

**O que isso libera:** seu avatar do MMD está pronto para o VRChat. Você pode adicionar física de cabelo (guia 6) e configurar a sincronia labial (guia 8) antes de enviar.

---

## Guia 4: corrija os nomes dos ossos do seu avatar

`CATS → VRChat Tools → VRChat Naming Extras`

> **Tempo:** cerca de 5–15 minutos
> **Resultado:** os ossos de que o VRChat precisa renomeados com nomes compatíveis com o VRChat

**Antes de começar, verifique:**
- [ ] Seu avatar está aberto e o esqueleto (armadura) está visível

---

### Passo 1 — Detectar o estilo de nomes atual

Na aba **CATS**, expanda **VRChat Tools** → **VRChat Naming Extras** (extras de nomes do VRChat) e clique em **Detectar**. O BoneCraft mostra o estilo de nomes encontrado (por exemplo Mixamo, VRoid ou Unity) e uma pontuação; **Forçar Nova Varredura** verifica de novo depois que você muda nomes.

Para nomes de ossos em japonês, chinês, coreano, português, espanhol ou francês, use em vez disso a aba **CATS** → **CATS** → **Traduzir Nomes de Ossos**: escolha o **Idioma** e execute. Ele converte os nomes para inglês em um só passo.

---

### Passo 2 — Renomear com os nomes do VRChat

Mapeie primeiro os ossos (guia 5, passo 2) e depois clique em **Normalize Names** em **Configurar Ossos Humanóides**: cada osso mapeado recebe o nome que o VRChat espera.

**O que você deve ver:** nomes de ossos como `Hips`, `Spine`, `Chest` e `LeftUpperArm`.

---

### Passo 3 — Correções manuais (se necessário)

**VRChat Naming Extras** também tem ferramentas em lote para os ossos restantes:

- **Localizar e Substituir** — troca um trecho de texto por outro em cada nome de osso
- **Adicionar Prefixo** e **Adicionar Sufixo** — adicionam texto ao início ou ao fim de cada nome de osso
- **Remover Prefixo** e **Remover Sufixo** — tiram esse texto de novo
- **Substituição por Regex** — o mesmo, com uma expressão regular

**O que isso libera:** nomes de ossos corretos fazem o mapeamento humanoide (guia 5) funcionar automaticamente. Sem eles, o VRChat não sabe como seu personagem deve se mover.

---

## Guia 5: mapeie seu avatar para o sistema corporal do VRChat

`CATS → Avatar Tools → Set Up Humanoid Bones`

> **Tempo:** cerca de 10–15 minutos
> **Resultado:** o esqueleto do seu avatar conectado ao sistema de movimento humanoide do VRChat

**Antes de começar, verifique:**
- [ ] Os ossos do seu avatar têm nomes razoáveis (se não, veja o guia 4)
- [ ] O esqueleto está selecionado
- [ ] Você está no **Modo Objeto** (veja o menu suspenso no canto superior esquerdo da viewport)

---

### Passo 1 — Abrir Configurar Ossos Humanóides

Na aba **CATS**, expanda **Avatar Tools** → **Configurar Ossos Humanóides**.

---

### Passo 2 — Mapeamento automático

Clique em **Mapear Tudo Automaticamente**. O BoneCraft examina seu esqueleto e preenche os slots do corpo.

> Um slot humanoide é como um gancho etiquetado que o VRChat usa: "o quadril vai aqui, a cabeça vai aqui, a mão esquerda vai aqui". O BoneCraft associa seus ossos a esses ganchos. Agora o mapeamento humanoide é lido corretamente de novo quando você reabre um arquivo.

**O que você deve ver:** os slots obrigatórios (15: Hips, Spine, Head, os dois braços, antebraços, mãos, coxas, pernas e pés) e os opcionais (Chest, UpperChest, Neck e outros), cada um com um osso, e a parcela de slots obrigatórios preenchidos.

---

### Passo 3 — Verificar o mapeamento

Clique em **Validar**. O BoneCraft verifica se cada slot obrigatório tem um osso e se a hierarquia faz sentido.

---

### Passo 4 — Preencher à mão os slots vazios

Um slot sem osso mostra "(click to map)" (clique para mapear). Clique nele e escolha o osso certo. Depois clique de novo em **Validar**, e em **Normalize Names** para que os ossos mapeados recebam os nomes do VRChat.

---

### Passo 5 — Configurar o rastreamento ocular (opcional)

Se seu avatar tem ossos dos olhos, use a aba **CATS** → **CATS** → **Rastreamento Ocular**: clique em **Detecção Automática** para encontrar os ossos dos olhos (ou escolha os ossos **Olho Esquerdo** e **Olho Direito**), defina os limites e clique em **Criar Rastreamento Ocular**. O [guia 13, fase 3](03-guides-b.md#fase-3--rastreamento-ocular) explica os ajustes.

**O que isso libera:** com o mapeamento humanoide feito, seu avatar se move corretamente no VRChat: o IK (cinemática inversa, o sistema que faz suas mãos no jogo seguirem seus controles reais) funciona, e seu avatar acompanha seus movimentos reais.

---

## Guia 6: adicione física de cabelo

`CATS → Avatar Tools → Add Hair Physics`

> **Tempo:** cerca de 15–25 minutos
> **Resultado:** o cabelo do seu avatar (e outras partes macias) balançando naturalmente no VRChat

**Antes de começar, verifique:**
- [ ] Seu avatar está aberto com o esqueleto selecionado
- [ ] Configurar Ossos Humanóides está feito (guia 5)

> PhysBone = o componente do VRChat que faz os ossos quicarem e balançarem como se tivessem peso. O BoneCraft os configura em cadeias de ossos: cabelo, orelhas, caudas, saias e acessórios.

---

### Passo 1 — Abrir Adicionar Física de Cabelo

Na aba **CATS**, expanda **Avatar Tools** → **Adicionar Física de Cabelo**. Ele tem quatro partes: Hair Chain Detection (detecção de cadeias de cabelo), Hair Chain Generation (geração de cadeias de cabelo), PhysBone Configuration (configuração de PhysBone) e Hair Physics Colliders (colisores de física de cabelo).

---

### Passo 2 — Encontrar as cadeias de cabelo

Se seu cabelo já tem ossos, clique em **Detect Hair Physics Chains** (detectar cadeias de física de cabelo). O BoneCraft encontra as cadeias de ossos que parecem cabelo (ossos ligados ponta a ponta a partir de uma raiz) e lista cada uma com o osso raiz e o comprimento.

Se seu cabelo ainda não tem ossos, selecione as malhas do cabelo e use Hair Chain Generation: escolha a **Densidade** (Low, Medium ou High: quantas cadeias) e clique em **Gerar**. **Substituir** as cria de novo com uma nova densidade.

---

### Passo 3 — Escolher um preset de PhysBone

Selecione um osso de uma cadeia. Em PhysBone Configuration, clique no preset adequado: **Cabelo**, **Saia** (saias e capas) ou **Cauda** (caudas e cordas).

**O que você deve ver:** os parâmetros da cadeia: Pull, Spring, Stiffness, Gravity e Max Angle.

---

### Passo 4 — Ajuste fino (opcional)

O painel mostra os valores da cadeia; ele não os edita. Mais Stiffness faz dobrar menos, mais Gravity puxa para baixo, um Max Angle menor limita o balanço. Para outros valores, clique em outro preset, ou mude o componente PhysBone no Unity depois de importar o avatar.

---

### Passo 5 — Adicionar colisores (recomendado)

Colisores são formas invisíveis que impedem o cabelo de atravessar a cabeça e o corpo. Em Hair Physics Colliders, clique em **Place Default Colliders** (posicionar colisores padrão) para adicionar colisores padrão na cabeça, nos ombros e no peito. **Add Collider** (adicionar colisor) e **Remove Collider** (remover colisor) adicionam ou removem um de cada vez.

**O que isso libera:** o cabelo do seu avatar agora se move naturalmente no VRChat quando você vira a cabeça, pula ou dança. Os mesmos passos servem para caudas, orelhas, saias e acessórios pendurados.

---

## Guia 7: anexe roupas que se movem com seu corpo

`CATS → VRChat Tools → Attach Clothing`

> **Tempo:** cerca de 20–30 minutos
> **Resultado:** uma peça de roupa presa ao esqueleto do seu avatar, movendo-se com seu corpo

**Antes de começar, verifique:**
- [ ] Seu avatar base tem um esqueleto pronto, e o corpo dele tem pesos pintados
- [ ] A roupa está no mesmo arquivo (com a própria armadura, se veio com uma)
- [ ] A roupa se ajusta mais ou menos ao corpo do seu avatar

---

### Passo 1 — Abrir Anexar Roupa

Na aba **CATS**, expanda **VRChat Tools** → **Anexar Roupa**. Ele tem três partes: Bone Matching (correspondência de ossos), Collision Detection (detecção de colisões) e Clothing Merge (mesclagem de roupas).

---

### Passo 2 — Corresponder os ossos

Se a roupa veio com a própria armadura, selecione-a e clique em **Corresponder ossos**. O BoneCraft associa cada osso da roupa ao osso equivalente do seu avatar (o braço esquerdo da roupa com o braço esquerdo do avatar, e assim por diante).

**O que você deve ver:** uma lista de pares de ossos: osso da roupa → osso do avatar. Para roupas sem armadura, pule este passo.

---

### Passo 3 — Mesclar a roupa

Selecione a roupa (a armadura e as malhas dela, ou só as malhas se ela não tiver armadura) e, por último, clique com Shift na armadura do seu avatar para que ela seja o objeto ativo. Clique em **Mesclar Roupas**. Com uma armadura de roupa, o BoneCraft passa a roupa para o seu esqueleto e mescla os ossos; sem ela, ele transfere os pesos do seu corpo para as malhas da roupa.

> Pesos (pintura de pesos) = números que dizem a cada ponto de uma malha quanto cada osso o move. Se sua manga esquerda tem peso no osso do braço esquerdo, mover esse osso puxa a manga junto.

**O que você deve ver:** a roupa sob o esqueleto do seu avatar. Mover um osso move o corpo e a roupa juntos.

---

### Passo 4 — Verificar as atravessadas

Clique em **Detectar colisões** para encontrar os lugares em que a roupa atravessa o corpo. Corrija-os ajustando os pesos ali (veja as ferramentas de pesos em [Ferramentas de rig](05-rig-tools.md)).

**O que isso libera:** roupas que se movem naturalmente com seu corpo. Repita para cada peça da roupa.

Próximo: [Guias 8–13](03-guides-b.md)
