# Guias 1–7

[← Conteúdo](index.md)

## Guia 1: leve seu primeiro avatar para o VRChat

Para uma malha prática antes de usar seu próprio avatar, siga o [oficina de manequim ilustrado](06-rig-builder.md#oficina-de-manequins-ilustrados): Simple Human, um manequim sem rig, Auto-Rig e depois IK/FK.

> **Tempo:** Cerca de 45 a 60 minutos para uma primeira execução completa
> **Resultado:** Um avatar manipulado e pronto para VRChat exportado para o SDK VRChat

**Antes de começar - verifique estes:**
- [] Seu modelo 3D é importado para Bforartists (Arquivo> Importar, escolha seu formato)
- [] O modelo está em pose de T (braços estendidos para os lados, corpo ereto) - ou próximo a isso
- [] O modelo não possui geometria quebrada óbvia (sem triângulos flutuantes aleatórios)
- [] Você pode ver seu modelo na janela de visualização 3D como uma forma cinza sólida

---

### Passo 1 — Abrir o Construtor de Rig

Abra a guia **Rig Builder** na prateleira de ferramentas esquerda (pressione**T** na viewport 3D). O mesmo Rig Builder está na guia**Properties** do editor**Scene** enquanto Preferences → Tabs → Scene Properties → Show está ativado. Possui três partes:**Auto-Rig Wizard**, Quick Rig (armaduras prontas) e**Mannequin**.

Expanda **Auto-Rig Wizard** e clique em**Start Auto-Rig**.

Você também pode iniciar o assistente no menu Adicionar → Armadura → Auto-Rig Wizard da viewport 3D e continuar no Rig Builder.

---

### Passo 2 — Selecionar sua malha

O assistente lista as malhas na cena. Clique na malha do seu avatar nessa lista e clique em **Next**.

**O que você deve ver:** Uma linha "Selected:" com o nome da sua malha e, em seguida, a etapa do tipo de rig.

---

### Passo 3 — Escolher o tipo de rig

Clique em **Body + Face** para um avatar cujo rosto você deseja animar (piscadas, expressões, sincronização labial) ou**Body Only** para um corpo sem controles faciais. Em Opções de geração,**Kinematics** define IK/FK, somente IK ou somente FK. Clique em**Next**.

---

### Passo 4 — Posicionar os marcadores do corpo

Este é o passo mais importante. Os marcadores são pontos que mostram BoneCraft onde está cada articulação principal: a pélvis, a coluna, o pescoço e a cabeça, os ombros, os braços, as mãos, as pernas e os pés. BoneCraft retira os ossos deles.

**A maneira rápida:** na caixa Detecção inteligente, clique em**Detect Markers**. BoneCraft traça os membros em sua malha e coloca cada marcador, cada um com confiança. Clique em**Accept High** para manter os seguros e em**Reset Low** para eliminar os duvidosos para que você mesmo possa colocá-los.**Guess Markers from Mesh** é uma estimativa mais simples a partir das proporções da malha.

**Com a ferramenta viewport:** para colocar vários marcadores, ative Place Rig Markers na barra de ferramentas da viewport no Object Mode. O cabeçalho da ferramenta nomeia o próximo marcador e possui bloqueios de eixo e uma chave de espelho. Clique na malha para posicionar e confirmar esse marcador; a ferramenta passa para o próximo marcador não confirmado. Quando a etapa for concluída, clique em**Next** no assistente.

**Um marcador por vez:** cada marcador possui uma linha de botões de ícones. Passe o mouse sobre um botão para ler sua dica de ferramenta.

1. Clique em **Place Marker** (o ícone de seta) na linha do marcador e, a seguir, clique no local certo em seu avatar.
2. Clique em **Confirm Marker** (a marca de seleção) quando estiver posicionado corretamente.**Reset Marker** (a seta circular) limpa um marcador colocado para que você possa colocá-lo novamente.

**Simetria:** **Toggle Symmetry** (o primeiro ícone na linha do marcador esquerdo ou direito) coloca o marcador do outro lado sempre que você posiciona este.**Mirror L to R** e**Mirror R to L** copiam todos os marcadores confirmados para o outro lado.

Quando cada marcador for colocado, clique em **Confirm All Placed** e depois em**Next**.

---

### Passo 5 — Posicionar os marcadores dos dedos

Em Detalhes dos dedos, escolha quantos dedos construir: "5 — Mão humana completa" para uma mão padrão ou menos (até "0 — Sem dedos"). Clique em **Guess Finger Markers**. BoneCraft encontra cada dedo no formato da mão e o traça da articulação até a ponta do dedo. Ajuste qualquer marcador que esteja desativado e clique em**Next**.

---

### Passo 6 — Posicionar os marcadores do rosto (só Body + Face)

Clique em **Guess Face Markers** e ajuste os olhos, pálpebras, sobrancelhas, cantos da boca e mandíbula conforme necessário. Os marcadores oculares ficam onde você os colocou. Clique em**Next**.

---

### Passo 7 — Revisar e gerar

A etapa de revisão lista todos os avisos e as opções de geração. Clique em **Generate Rig**.

**O que você deveria ver:** Um esqueleto (ossos laranja) dentro do seu avatar, com membros IK/FK, ossos de dedos e, para um rig Body + Face, um rig facial e a pele do seu avatar presa a ele para que se deforme quando os ossos se movem. A última etapa oferece**Build Control Rig** para as opções de revisão Generate Rig não se aplica e**Close Wizard**; [Construtor de plataforma](06-rig-builder.md) descreve ambos.

> **Pesos de pele** = números que decidem quais ossos movem quais partes da malha do seu avatar. BoneCraft os configura automaticamente; você pode refiná-los com as ferramentas de peso (consulte [Ferramentas de plataforma](05-rig-tools.md) ).

---

### Passo 8 — Mapear para os ossos humanoides do VRChat

Abra a guia **CATS** na barra lateral direita (pressione**N**), expanda**Avatar Tools** e depois**Set Up Humanoid Bones**. Clique em**Auto-Map All**: BoneCraft conecta seus ossos aos slots do corpo que VRChat usa para mover um avatar com você. Clique em**Normalize Names** para dar aos ossos mapeados os nomes que VRChat espera e, em seguida,**Validate**.

**O que você deve ver:** Cada um dos slots necessários (quadril, coluna, cabeça, braço esquerdo e assim por diante) mostra um osso. O Guia 5 explica os slots.

---

### Passo 9 — Exportar para o VRChat

Na guia **CATS**, expanda**Avatar Tools** →**Export to VRChat**. Defina o nome**Folder** e**Avatar** e clique em**Export to VRChat (Unity)**.

**O que você deveria ver:** O avatar exportado na pasta escolhida, pronto para o VRChat Creator Companion e o SDK VRChat em Unity.

---

**O que isso desbloqueia:** Agora você tem um avatar VRChat manipulado. A partir daqui você pode adicionar física do cabelo (Guia 6), anexar roupas (Guia 7), configurar sincronização labial (Guia 8) e verificar o desempenho (Guia 9). Para uma limpeza completa e configuração do VRChat com as ferramentas CATS, consulte [Guia 13](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats).

---

## Guia 2: leve um avatar do VRoid para o VRChat

> **Tempo:** Cerca de 15–25 minutos
> **Resultado:** Seu avatar VRoid pronto para exportação VRChat

**Antes de começar - verifique estes:**
- [] Você exportou seu avatar do VRoid Studio como um arquivo `.vrm` ou baixou-o do VRoid Hub como um `.zip`
- [] BoneCraft está instalado e habilitado

---

### Passo 1 — Instalar o add-on VRM

BoneCraft usa o complemento VRM para ler arquivos `.vrm`. Na guia **CATS**, expanda**Import / Export** →**VRM / VRoid**. Se disser que o complemento não está instalado, clique em**Auto-Install Latest from GitHub**. Sem conexão com a internet, baixe você mesmo o complemento e use**Install from.zip on Disk…**;**Open Extensions Page** abre sua página de download.

---

### Passo 2 — Importar seu avatar

Na mesma seção **VRM / VRoid**, clique em**Import VRM…** e escolha seu arquivo `.vrm`. Para baixar VRoid, clique em**Import VRoid (.vroid /.zip)…** e escolha `.zip`.

Se você escolher um arquivo de projeto VRoid Studio (`.vroid` ), BoneCraft mostrará um cartão "VRoid Studio Project": um projeto ainda não é um avatar. Exporte-o para VRM no VRoid Studio e importe esse arquivo.

**O que você deveria ver:** Seu personagem VRoid na janela de visualização com seu esqueleto no lugar.

---

### Passo 3 — Mapear para os ossos humanoides do VRChat

Na guia **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, clique em**Auto-Map All**. Os esqueletos VRoid seguem um layout padrão, portanto, geralmente preenche todos os slots. Se um slot estiver errado,**Fix Humanoid Map** na seção**VRM / VRoid** (em Lint) repara as confusões usuais de nomes VRoid.

---

### Passo 4 — Corrigir os nomes dos ossos

Clique em **Normalize Names** em**Set Up Humanoid Bones**. VRoid tem seus próprios nomes de ossos; isso dá aos ossos mapeados os nomes que VRChat espera.

---

### Passo 5 — Configurar os visemas (sincronia labial)

Os avatares VRoid já possuem formatos de boca para sincronização labial. Na seção **VRM / VRoid**, clique em**Map VRoid Visemes**. BoneCraft corresponde às chaves de forma de VRoid com as formas de sincronização labial de VRChat.

---

### Passo 6 — Física de cabelo (opcional)

O cabelo VRoid usa SpringBones. **Convert SpringBones → PhysBones** na seção**VRM / VRoid** os transforma em VRChat PhysBones. O Guia 6 cobre a física do cabelo com mais detalhes.

---

### Passo 7 — Exportar

Exporte como no Guia 1, Etapa 9.

**O que isso desbloqueia:** Seu avatar VRoid está pronto para o VRChat Creator Companion. Você também pode verificar o desempenho (Guia 9) antes de fazer upload.

---

## Guia 3: leve um avatar do MMD para o VRChat

> **Tempo:** Cerca de 20–30 minutos
> **Resultado:** Seu modelo MMD `.pmx` pronto para VRChat

**Antes de começar - verifique estes:**
- [] Você tem um arquivo de modelo `.pmx` ou `.pmd` MMD
- [] BoneCraft está instalado

---

### Passo 1 — Instalar o mmd_tools

BoneCraft usa o complemento mmd_tools para ler arquivos MMD. Na guia **CATS**, expanda**Import / Export** →**MMD / PMX**. Se disser que mmd_tools não está instalado, clique em**Auto-Install Latest from GitHub** (ou**Install from.zip on Disk...** com uma cópia baixada).

---

### Passo 2 — Importar seu arquivo PMX

Na seção **MMD / PMX**, clique em**Import PMX / PMD...** e escolha seu modelo.

**O que você deveria ver:** Seu personagem MMD na janela de visualização com nomes de ossos japoneses.

---

### Passo 3 — Corrigir os nomes dos ossos

VRChat não pode ler os nomes dos ossos japoneses de MMD. Na seção **MMD / PMX**, clique em**Convert Bone Names -> Unity**. Para nomes em outro idioma, use a guia**CATS** →**CATS** →**Translate Bone Names**: escolha o**Language** e execute-o.

---

### Passo 4 — Limpar o modelo

Os modelos MMD geralmente possuem geometria extra e muitas peças separadas. Na guia **CATS** →**CATS**, execute**Fix Model** primeiro e depois**Join Meshes** para combinar as partes do corpo em uma malha (recomendado para VRChat ). [Guia 13](03-guides-b.md#guia-13-prepare-seu-avatar-para-o-vrchat-com-o-cats) percorre todo o pipeline CATS em ordem.

---

### Passo 5 — Mapear para os ossos humanoides do VRChat

Na guia **CATS** →**Avatar Tools** →**Set Up Humanoid Bones**, clique em**Auto-Map All**. Os esqueletos MMD são próximos aos do VRChat, portanto, a maioria dos slots é preenchida automaticamente. Para um slot vazio, clique no botão e escolha o osso.

---

### Passo 6 — Física e exportação

**Convert Physics -> PhysBones** na seção**MMD / PMX** transforma o cabelo do corpo rígido e a física da saia de MMD em VRChat PhysBones. Em seguida, exporte como no Guia 1, Etapa 9.

**O que isso desbloqueia:** Seu avatar MMD está pronto para VRChat. Você pode adicionar a física do cabelo (Guia 6) e configurar a sincronização labial (Guia 8) antes de enviar.

---

## Guia 4: corrija os nomes dos ossos do seu avatar

> **Tempo:** Cerca de 5–15 minutos
> **Resultado:** Os ossos VRChat precisam ser renomeados para nomes compatíveis com VRChat

**Antes de começar - verifique estes:**
- [] Seu avatar está aberto com seu esqueleto (armadura) visível

---

### Passo 1 — Detectar o estilo de nomes atual

Na guia **CATS**, expanda**VRChat Tools**, encontre seu grupo Naming e clique em**Detect**. BoneCraft mostra o estilo de nomenclatura encontrado (por exemplo Mixamo, VRoid ou Unity ) e uma pontuação;**Force Rescan** verifica novamente após você alterar os nomes.

Para nomes de ossos em japonês, chinês, coreano, português, espanhol ou francês, use a guia **CATS** →**CATS** →**Translate Bone Names**: escolha o**Language** e execute-o. Ele converte os nomes para inglês em uma única etapa.

---

### Passo 2 — Renomear com os nomes do VRChat

Mapeie os ossos primeiro (Guia 5, Etapa 2) e, em seguida, clique em **Normalize Names** em**Set Up Humanoid Bones**: cada osso mapeado recebe o nome esperado por VRChat.

**O que você deveria ver:** Nomes de ossos como `Hips`, `Spine`, `Chest` e `LeftUpperArm`.

---

### Passo 3 — Correções manuais (se necessário)

O grupo Naming em **VRChat Tools** também possui ferramentas em lote para os ossos restantes:

- **Find and Replace** — substitua um pedaço de texto por outro em cada nome de osso
- **Add Prefix** e**Add Suffix** — adicione texto ao início ou ao final de cada nome de osso
- **Remove Prefix** e**Remove Suffix** – retire-o novamente
- **Regex Replace** — o mesmo, com uma expressão regular

**O que isso desbloqueia:** Os nomes corretos dos ossos permitem que o mapeamento humanóide (Guia 5) funcione automaticamente. Sem eles, VRChat não consegue dizer como seu personagem deve se mover.

---

## Guia 5: mapeie seu avatar para o sistema corporal do VRChat

> **Tempo:** Cerca de 10–15 minutos
> **Resultado:** O esqueleto do seu avatar conectado ao sistema de movimento humanóide de VRChat

**Antes de começar - verifique estes:**
- [] Os ossos do seu avatar são nomeados de forma sensata (consulte o Guia 4 se não)
- [] O esqueleto está selecionado
- [] Você está em **Object Mode** (verifique o menu suspenso no canto superior esquerdo da janela de visualização)

---

### Passo 1 — Abrir Configurar Ossos Humanóides

Na guia **CATS**, expanda**Avatar Tools** →**Set Up Humanoid Bones**.

---

### Passo 2 — Mapeamento automático

Clique em **Auto-Map All**. BoneCraft examina seu esqueleto e preenche as ranhuras do corpo.

> Um slot humanóide é como um gancho rotulado que VRChat usa: "Os quadris vão aqui, a cabeça vai aqui, a mão esquerda vai aqui." BoneCraft combina seus ossos com esses ganchos. O mapeamento humanóide agora é lido corretamente quando você reabre um arquivo.

**O que você deve ver:** Os slots obrigatórios (15: quadris, coluna, cabeça, braços, antebraços, mãos, coxas, pernas e pés) e os opcionais (peito, tórax superior, pescoço e outros), cada um com um osso, e a parcela de slots obrigatórios que são preenchidos.

---

### Passo 3 — Verificar o mapeamento

Clique em **Validate**. BoneCraft verifica se cada slot necessário possui um osso e se a hierarquia faz sentido.

---

### Passo 4 — Preencher à mão os slots vazios

Um slot sem osso mostra "(clique para mapear)". Clique nele e escolha o osso certo. Em seguida, clique em **Validate** novamente e em**Normalize Names** para que os ossos mapeados obtenham os nomes de VRChat.

---

### Passo 5 — Configurar o rastreamento ocular (opcional)

Se o seu avatar tiver ossos oculares, use a guia **CATS** →**CATS** →**Eye Tracking**: clique em**Auto-Detect** para encontrar os ossos oculares (ou escolha os ossos**Left Eye** e**Right Eye** ), defina os limites e clique**Create Eye Tracking**. [Guia 13, Fase 3](03-guides-b.md#fase-3--rastreamento-ocular) explica as configurações.

**O que isso desbloqueia:** Com o mapeamento humanóide concluído, seu avatar se move corretamente em VRChat: IK (cinemática inversa, o sistema que faz com que suas mãos no jogo sigam seus controladores reais) funciona, e seu avatar segue seus movimentos do mundo real.

---

## Guia 6: adicione física de cabelo

> **Tempo:** Cerca de 15–25 minutos
> **Resultado:** O cabelo do seu avatar (e outras partes moles) balançando naturalmente em VRChat

**Antes de começar - verifique estes:**
- [] Seu avatar está aberto com o esqueleto selecionado
- [] A configuração dos ossos humanóides está concluída (Guia 5)

> PhysBone = VRChat componente que faz os ossos saltarem e balançarem como se tivessem peso. BoneCraft os monta em correntes de ossos: cabelos, orelhas, rabos, saias e acessórios.

---

### Passo 1 — Abrir Adicionar Física de Cabelo

Na guia **CATS**, expanda**Avatar Tools** →**Add Hair Physics**. Possui quatro partes: Detecção de Cadeia Capilar, Geração de Cadeia Capilar, Configuração PhysBone e Colisores de Física Capilar.

---

### Passo 2 — Encontrar as cadeias de cabelo

Se o seu cabelo já tem ossos, clique em **Detect Hair Physics Chains**. BoneCraft encontra as cadeias de ossos que parecem cabelos (ossos ligados de ponta a ponta a partir de uma raiz) e lista cada uma com seu osso e comprimento da raiz.

Se seu cabelo ainda não tem espinhas, selecione as malhas de cabelo e use Geração de Cadeia de Cabelo: escolha o **Density** (Baixo, Médio ou Alto: quantas correntes), depois clique em**Generate**.**Replace** os constrói novamente com uma nova densidade.

---

### Passo 3 — Escolher um preset de PhysBone

Selecione um osso de uma corrente. Em Configuração PhysBone, clique na predefinição adequada: **Hair**,**Skirt** (saias e capas) ou**Tail** (caudas e cordas).

**O que você deveria ver:** Os parâmetros da corrente: Tração, Mola, Rigidez, Gravidade e Ângulo Máximo.

---

### Passo 4 — Ajuste fino (opcional)

O painel mostra os valores da cadeia; ele não os edita. Mais rigidez faz com que a corrente dobre menos, mais gravidade a puxa para baixo e um ângulo máximo menor limita a distância que ela oscila. Para valores diferentes, clique em outra predefinição ou altere o componente PhysBone em Unity após importar o avatar.

---

### Passo 5 — Adicionar colisores (recomendado)

Colliders são formas invisíveis que impedem que o cabelo passe pela cabeça e pelo corpo. Em Hair Physics Colliders, clique em **Place Default Colliders** para adicionar colisores padrão na cabeça, ombros e peito.**Add Collider** e**Remove Collider** adicionam ou removem um de cada vez.

**O que isso desbloqueia:** O cabelo do seu avatar agora se move naturalmente em VRChat quando você vira a cabeça, pula ou dança. Os mesmos passos funcionam para rabos, orelhas, saias e acessórios pendurados.

---

## Guia 7: anexe roupas que se movem com seu corpo

> **Tempo:** Cerca de 20–30 minutos
> **Resultado:** Uma peça de roupa presa ao esqueleto do seu avatar, movendo-se com o seu corpo

**Antes de começar - verifique estes:**
- [] Seu avatar base tem um esqueleto acabado e seu corpo é pintado com peso
- [] A peça de roupa está no mesmo arquivo (com armadura própria se vier com uma)
- [] A roupa se ajusta aproximadamente ao corpo do seu avatar

---

### Passo 1 — Abrir Anexar Roupa

Na guia **CATS**, expanda**VRChat Tools** e encontre seu grupo Roupas. Possui três partes: Combinação de Ossos, Detecção de Colisão e Mesclagem de Roupas.

---

### Passo 2 — Corresponder os ossos

Se a roupa veio com armadura própria, selecione-a e clique em **Match Bones**. BoneCraft emparelha cada osso da roupa com o osso equivalente do seu avatar (o braço esquerdo da roupa com o braço esquerdo do seu avatar e assim por diante).

**O que você deveria ver:** Uma lista de pares de ossos: osso de roupa → osso de avatar. Para roupas sem armadura, pule esta etapa.

---

### Passo 3 — Mesclar a roupa

Selecione a roupa - sua armadura e malhas, ou apenas suas malhas se não tiver armadura - e clique com a tecla Shift pressionada na armadura do seu avatar por último, para que seja o objeto ativo. Clique em **Merge Clothing**. Com uma armadura de roupa, BoneCraft move a roupa para o seu esqueleto e funde os ossos; sem ele, ele transfere o peso do seu corpo para as malhas da roupa.

> Pesos (pintura de pesos) = números que informam a cada ponto de uma malha o quanto cada osso a movimenta. Se a manga esquerda pesa sobre o osso do braço esquerdo, mover esse osso puxa a manga junto.

**O que você deveria ver:** As roupas sob o esqueleto do seu avatar. Mover um osso move tanto o corpo quanto a roupa.

---

### Passo 4 — Verificar as atravessadas

Clique em **Detect Collisions** para encontrar locais onde as roupas atravessam o corpo. Corrija-os ajustando os pesos (veja as Ferramentas de Peso em [Ferramentas de plataforma](05-rig-tools.md) ).

**O que isso desbloqueia:** Roupas que se movem naturalmente com seu corpo. Repita para cada peça de roupa.

Próximo: [Guias 8–13](03-guides-b.md)
