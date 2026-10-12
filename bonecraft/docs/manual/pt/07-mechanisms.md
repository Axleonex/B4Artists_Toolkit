# Mechanisms (mecanismos)

[← Conteúdo](index.md)

## O que o Mechanisms faz

Os mecanismos transformam peças de superfície dura em um rig mecânico funcional: dobradiças,
slides, telescópios, pistões, engrenagens, seguidores e transformações inteiras jogadas
por um controle deslizante. Ele constrói ossos e restrições Blender comuns, para que você possa ver
e mude tudo o que ele faz, e o rig funciona em Blender sem scripts.
Os motores recebem os ossos `DEF-`. Exportação de movimento de mecanismo cozido para motores
vem depois (veja Limites desta versão).

BoneCraft envia as ferramentas, não uma arma. Você traz as peças.

Um exemplo completo e funcional, com uma captura de tela para cada etapa, é [Tutorial: Crescent Rose com mecanismos](12-crescent-rose.md).

Palavras usadas nos painéis e nesta página:

|Palavra|Significado|
|---|---|
|*Parte*|Uma peça que se move como um bloco sólido: um objeto ou um pedaço solto de uma malha. Uma parte pode andar em outra parte.|
|*Conjunto*|Como uma peça pode se mover: Dobradiça (gira), Slide (move), Telescópio (estende segmentos aninhados).|
|*Link*|O que move uma peça para você: Pistão, Gear Link, Follow.|
|*Alça*|O osso que você arrasta na viewport. Cada junta tem uma. Seu valor também é um controle deslizante no painel.|
|*Sequência*|Uma transformação executada por um controle deslizante, feito de etapas.|
|*Formulário*|Um conjunto salvo de valores de alça e sequência, como "Stowed" ou "Rifle".|

## Onde fica

- **BoneCraft tab → Mechanisms** na viewport 3D. A guia BoneCraft está ativada
na prateleira de ferramentas esquerda (pressione **T**), a menos que você a tenha movido para a barra lateral direita
(**N**) em Preferências. Fica entre Skin e Review. Mostra quando uma malha
está ativo (para iniciar uma plataforma) ou quando uma armadura com mecanismos está ativa; caso contrário
explica o que selecionar.
- **Properties editor → Scene tab → Mechanisms**, logo após Rig Builder. É
mostrado enquanto Preferências → Guias → Propriedades da cena → Mostrar está ativado. Sem nada
utilizável selecionado mostra uma linha: "Selecione uma malha
para começar, ou uma armadura com mecanismos." Alternando a guia da janela de visualização BoneCraft
desligado não o remove. A opção Propriedades da cena oculta apenas a cópia da cena.
A chave de ferramenta `mechanisms` (**Preferências → Complementos → BoneCraft → Ferramentas**)
remove a ferramenta de todos os locais.
As seções da guia Cena começam recolhidas, então clique em **Mechanisms** para expandi-la.
- **Object menu → Mechanisms** fornece atalhos para adicionar peças, juntas e links,
e para testar o movimento.
- **Viewport toolbar → Build Mechanism** inicia uma junta guiada ou link a partir de um
clique em uma peça, no Modo Objeto ou Modo Pose. Adicione as peças primeiro e depois selecione
o equipamento do mecanismo ou uma de suas peças e escolha o tipo no cabeçalho da ferramenta.

Dentro dos Mecanismos existem quatro subseções: **1. Parts**,**2. Articulações e
Ligações**,**3. Sequências** e**4. Controles**. Eles aparecem assim que a rig
peças. Antes disso você vê apenas **Add Parts from Selection**.

Cada botão é uma etapa de desfazer. Se uma compilação falhar, tudo o que foi alterado será colocado
volta e o painel mostra o motivo.

## Peças

1. Selecione os objetos de peça (ou uma malha feita de peças soltas) no Modo de Objeto.
2. Clique em **Add Parts from Selection**.
 - Vários objetos: uma parte por objeto. Cada objeto é parente de sua parte
osso e permanece onde está.
 - Uma malha com peças soltas: uma parte por peça. Cada peça recebe um vértice
grupo para seu osso e a malha recebe um modificador de Armadura.
 - Na primeira vez, BoneCraft faz o equipamento (uma armadura) para você.
3. Selecione uma peça na lista para editá-la.

Para cada parte:

- **Passeios:** escolha a parte com a qual este se move. Uma parte filha segue seu
parte pai. "a plataforma" significa que ela fica na raiz da plataforma.
- **Size** define o comprimento do osso, que define o tamanho do cabo.
- **Edit Pivot** coloca um marcador na peça. Arraste-o para onde a peça deveria
gire ou deslize e clique em **Apply Pivot**. Os ossos da peça se movem para lá
e o objeto permanece no lugar.
- **Apply Transforms** aparece quando uma parte do objeto tem rotação não aplicada ou
escala. Clique nele. As transformações não aplicadas inclinam os eixos.
- O botão **X** remove a peça. Recusa enquanto um conjunto, link ou outro
parte o usa e os nomeia.
- **Merge for VRChat** (duas ou mais partes do objeto) une as partes do objeto em
uma malha com um grupo de vértices por objeto anterior e um modificador Armature.
Faça isso por último. As partes unidas tornam-se partes soltas daquela malha. Isso
remove todos os grupos de vértices nomeados após um osso desta armadura (exceto
osso `DEF-` da própria peça), portanto, mescle apenas as peças que estão montadas no
equipamento de mecanismo sozinho.

Você pode renomear o objeto de uma peça: as peças são marcadas em seus objetos, então a peça
encontra seu objeto novamente. Uma cópia do objeto (Shift+D) não assume o controle
parte. Se o objeto de uma peça for excluído, a peça mostrará "Parte '<nome>' ausente"
com **Reassign** e**Delete**. Outros mecanismos continuam funcionando.

- **Reassign** usa a malha que você selecionou. Ele recusa uma não-malha e
recusa um objeto que outra parte do objeto já utiliza. Partes soltas de um
mesh pode compartilhar essa malha.
- **Delete** remove a peça (veja a edição abaixo para saber quando ela é recusada).

## Articulações e ligações, um exemplo de cada

Adicione uma junta com **Add Joint**, um link com**Add Link**. Cada escolha inicia um
construção guiada. Eles funcionam na guia viewport e na cena do editor de propriedades
guia; na guia Cena, o guia usa a maior viewport 3D da tela.
Alternativamente, ative o Build Mechanism na barra de ferramentas da viewport, escolha a junta
ou tipo de link no cabeçalho da ferramenta e clique na primeira parte. Esse clique inicia o
mesmo guia e fornece sua primeira escolha. Continue com as escolhas e opções de eixo
solicitado na janela de visualização; os menus Adicionar junta e Adicionar link permanecem disponíveis.

Regras curtas para cada construção guiada:

- Clique nas peças na viewport. As partes clicadas recebem um contorno e um número.
- Onde uma etapa precisar de um eixo, pressione **X**,**Y** ou**Z** ou**A** para alinhar
a seleção. **Align to Selection** é para dobradiças angulares. Precisa da malha da peça
ainda estar no modo de edição com uma aresta ou face selecionada quando você pressiona **A**,
e o guia ignora **Tab**. Então entre no Modo de Edição na malha da peça e
selecione uma aresta ou face primeiro. Permaneça no modo de edição, inicie **Adicionar junta →
Dobradiça**, clique na peça e pressione**A**. Se nada utilizável for selecionado, o guia
informa e você pode pressionar outra tecla.
- A última etapa mostra o mecanismo se movendo em loop. **Enter** mantém.
**Esc** o remove.
- O cabeçalho e a barra de status mostram uma frase completa para cada etapa. Com exposição
Os ajudantes mostram uma pequena etiqueta.

Cada linha da lista Juntas e Ligações possui quatro botões de ícone: **Test** (reproduzir
triângulo), **Edit** (lápis, mostra as configurações),**Detach** (corrente quebrada) e
**Delete** (X).

Após a construção, o item selecionado na lista mostra apenas as configurações
tipo usa.

### Hinge (dobradiça)

Dobradiça da lâmina, 0°…90°:

1. Adicione peças da seleção com uma peça Blade.
2. **Add Joint → Hinge**. Clique na lâmina. Pressione**X**. Pressione**Enter**.
3. Você obtém uma alça de semicírculo, `CTRL-Blade`, e uma *Dobradiça de Lâmina* no
lista. Defina **Min** 0 e**Max** 90 (° para uma dobradiça).
4. Experimente: arraste a alça em semicírculo. Ele para em 90°. **Set Min** e
**Set Max** copia a pose atual do identificador para os limites.

Um limite que esteja abaixo de uma volta completa deve ficar entre −180°…180°. Limites como
170°…190° são recusados com uma mensagem. Um alcance de um turno completo ou mais (por
exemplo −180°…180°) gira livremente sem limite.

### Slide (deslizador)

Deslizamento do cano, 0…0,3:

1. **Add Joint → Slide**. Clique na parte Barril. Pressione**Y**. Pressione**Enter**.
2. Você recebe uma alça de flecha. Defina **Min** 0 e**Max** 0,3 (unidades de cena).
3. Experimente: arraste a seta. O cano desliza e para em 0,3.

### Telescope (telescópio)

Mastro com três segmentos:

1. Faça a base e três partes do segmento.
2. **Add Joint → Telescope**. Clique na base. Clique em cada segmento da base
para fora. Pressione **Enter**. Pressione a tecla do eixo. Pressione**Enter** para mantê-lo.
3. Você obtém uma alça de seta na base. **Length** é o percurso total;
**Shares (empty = even)** divide-o entre os segmentos. Para experimentar personalizado
compartilhamentos, defina **Length** como 1 primeiro e depois digite `0.5, 0.25, 0.25`. As ações
deve somar o Comprimento, para que a ponta percorra todo o comprimento. Um erro de digitação (por
exemplo `0.5, abc` ) é recusado com a mesma mensagem simples: as ações
devem ser números, um por segmento, que somam o Comprimento.
4. Experimente: arraste a seta. Todos os três segmentos se estendem por suas ações.
**Set Max** define o comprimento a partir da pose da alça.

### Piston (pistão)

Elevador: cilindro na estrutura, haste no braço.

1. Dê uma dobradiça ao braço primeiro e coloque-o para montar na estrutura.
2. **Add Link → Piston**. Clique na peça do cilindro (na moldura). Clique na haste
parte (no braço).
3. Você ganha um pistão sem alça. Cada parte aponta para o anexo da outra
ponto. **Stretch** (opcional) estica a haste, para molas e cabos.
4. Experimente: mova a alça do braço. O pistão segue. Se nada move o
Pistão ainda, a construção funciona, mas não tem visualização e **Test** diz isso.

### Gear Link (ligação de engrenagem)

Engrenagem 20:40:

1. Ambas as partes precisam primeiro de uma junta. A parte motriz precisa de uma dobradiça. Para equipamentos e
Correia a parte acionada precisa de uma dobradiça; para Rack é necessário um Slide.
2. **Add Link → Gear Link**. Clique na parte de direção. Clique na peça acionada.
3. Em suas configurações defina **Source Teeth** 20 e**Target Teeth** 40 (ou digite um
**Ratio** ).**Kind** é engrenagem, cinto ou rack.**Reverse** inverte a direção.
4. Experimente: ligue a fonte. Com **Kind** Gear o alvo gira −0,5× até
(+0,5× com Cinto). Uma engrenagem inverte
direção, um cinto o mantém e um rack transforma a rotação em um deslizamento (distância
por radiano = **Ratio** ×**Pinion Radius** ).

A forma como BoneCraft o constrói depende do intervalo da dobradiça de origem:

- Sob uma volta completa: uma restrição Transform. Segue tudo o que se move
a fonte, sequências incluídas.
- Uma volta completa ou mais: um driver que não precisa de Python. O alvo gira para sempre
com a fonte. Segue apenas alças e engrenagens. O validador da plataforma avisa
quando uma sequência ou acompanhamento seria perdido.

### Follow (seguidor)

A lâmina 0–90° levanta a tampa 0–40°:

1. Ambas as partes precisam de uma dobradiça ou corrediça. Uma dobradiça de origem precisa de limites sob um
volta completa; uma fonte de giro livre é recusada.
2. **Add Link → Follow**. Clique na parte principal (Lâmina). Clique no seguinte
parte (capa).
3. Os intervalos começam como o intervalo completo de cada articulação. Definir **Source Range**
0…90 e **Target Range** 0…40. Depois de qualquer uma das extremidades, o alvo se mantém.
4. Experimente: mova a alça da lâmina. A capa segue.
5. Marque **Curve** para remodelar o mapeamento no Editor de gráfico. BoneCraft nunca
substitui sua curva (veja Edição abaixo).

### Sequence (sequência)

Registre as etapas para dobrar uma arma:

1. Em **3. Sequences**, clique em**Add Sequence**. Faz uma alça deslizante
`CTRL-SEQ-<name>`.
2. Clique em **Move Slider to End**. O controle deslizante salta para o final (1) e o botão
torna-se Record Step seguido pelo próximo número da etapa.
3. Posicione as alças das juntas para o primeiro passo. Clique em Gravar Etapa 1.
Cada alça movida se torna uma etapa com seu valor alvo, e o
alças voltam a zero.
4. Repita as etapas 2 e 3 para mais etapas. Cada novo passo leva o próximo trimestre do
controle deslizante por padrão.
5. Defina **Target**, a facilidade (Linear, Ease In, Ease Out, Ease In Out, Snap),
**Start** e**End** para cada etapa. Fora de sua fatia, um degrau mantém seu fim
valor. Várias sequências podem ser empilhadas.
6. Clique em **Test**: o controle deslizante reproduz 0 → 1 → 0.

Ao lado do botão de gravação passo a passo e **Test**, a sequência selecionada tem**Detach**
(corrente quebrada) e **Delete** (X). Uma sequência mantida (por exemplo, uma etapa cuja
curva que você remodelou) mostra sua mensagem e um botão **Restore**. Restaurar
regenera as etapas do registro. Keep mine não é oferecido para uma sequência.

## Test

**Test** (o botão play na lista e em 3. Sequências) varre um
mecanismo em toda a sua extensão e costas. Não escreve teclas e faz pose
de volta quando terminar. Pressione **Esc** para interrompê-lo mais cedo; a pose é restaurada então
também. Para um Gear Link ou Follow, ele varre a fonte. Para um Pistão ele varre o
articulação que o move. Fique atento às peças que entram em conflito; BoneCraft não detecta
colisões.

## Formas

Em **4. Controls**:

- Cada junta e sequência possui um controle deslizante. É o próprio canal do identificador, então
arrastar a alça e usar o controle deslizante são a mesma coisa.
- **Save Form** registra cada identificador e valor do controle deslizante de sequência sob um nome.
Renomeie-o na lista.
- **Go to Form** define cada controle para os valores salvos.
- **Go and Key** faz o mesmo e também insere chaves no quadro atual.
- O **X** próximo à lista remove um formulário.

## O que o BoneCraft constrói

Para cada parte:

|Osso|Trabalho|Visível|
|---|---|---|
|`CTRL-<part>` |A alça. Seu valor é o controle deslizante do painel. Apenas Dobradiça, Slide e Telescópio fazem um.|Sim|
|`MCH-<part>` |Adiciona o identificador e todos os links e aplica os limites.|Oculto|
|`DEF-<part>` |Cópias `MCH-<part>`. A malha está ligada a ele. Os motores recebem esse osso.|Oculto|

Os ossos ficam nas coleções `Mechanism Controls`, `Mechanism MCH` e
`Mechanism DEF`. Uma peça sem junta possui apenas ossos `MCH-` e `DEF-`. Um
A alça do telescópio é `CTRL-<telescope name>`. Uma sequência é
`CTRL-SEQ-<name>`. Um pistão adiciona ossos `MCH-<part>-aim` e `MCH-<part>-target`
para cada uma de suas duas partes.

As restrições em `MCH-<part>` sempre vêm na mesma ordem: Copiar Transformações
da alça, depois a contribuição de cada link, depois o limite de rotação da junta
ou Limitar localização. `DEF-<part>` tem uma cópia de transformação de `MCH-<part>`.

Tudo o que BoneCraft compila é marcado com seu registro: nomes de restrições começam
com `BC·<id>·<role>`, e os ossos carregam as propriedades `bc_mech_id` e
`bc_mech_role`. BoneCraft encontra seus ossos por etiqueta, não por nome, para que você possa
renomeie qualquer osso. Uma reconstrução o encontra novamente e não duplica.

Com Show Helpers ativado, cada junta e link possui uma nota **How this works**. Isso
lista as restrições por nome, diz o que cada uma faz e tem um **Select**
botão (um ícone de seta) para inspecionar o osso.

Suas próprias restrições, motivadores e ossos nunca são tocados. Uma restrição que você adiciona
a um osso MCH permanece abaixo do BoneCraft após uma reconstrução.

## Edições e mudanças à mão

- **Edições de valor** (limites, proporção, intervalos, tempo, facilidade, aparência do identificador) atualizam o
restrições existentes. Não há reconstrução.
- **Edições estruturais** (um**Kind** do Gear Link, um**Curve** do Follow, um
**Stretch** do pistão) substitui as restrições desse mecanismo e reconstrui apenas
esse mecanismo.
- **Alterado manualmente.** Se você editar uma restrição BoneCraft (por exemplo, um
Limite), a mensagem do mecanismo termina com "(alterado manualmente)". BoneCraft nunca substitui
isso silenciosamente. Escolha:
 - **Keep mine** copia seus valores no registro. Recusa o que não pode
leia novamente e diga para usar Restaurar ou Desanexar.
 - **Restore** descarta sua edição e reconstrói a partir do registro.
- Um mecanismo retido também mantém todos os mecanismos que usam seus ossos, até que você
resolver isso.
- Uma curva remodelada é a mesma. Se você remodelar uma curva de Follow (**Curve**
marcada) no Editor de Gráfico e, em seguida, altere um valor que o substitua,
como seu intervalo alvo, a mensagem do Follow termina com "(alterado manualmente)". **Keep mine**
mantém sua curva. **Restore** o regenera.
- Uma sequência retida mostra sua mensagem e **Restore** em**3. Sequences**, com
**Detach** e**Delete** próximos a ele. Keep mine não é oferecido para sequências.
- **Detach** (botão de cadeia quebrada) exclui o registro e as tags, mas mantém os ossos e
restrições como seu próprio equipamento feito à mão. Desanexar e Excluir recusam um registro
que outro registro usa e nomeie os usuários.
- **Delete** (botão X) remove o registro e tudo que BoneCraft construiu para ele.
- Um loop de link é recusado antes que qualquer coisa seja construída, e o loop é nomeado, por
exemplo "Dobradiça da lâmina → Seguimento da tampa → Dobradiça da lâmina faria um loop."

O Rig Validator e o Task Board relatam loops de link, peças faltantes, DEF
ossos movidos de fora de seu mecanismo, drivers que precisam de Python e Gear
Links que perdem uma sequência ou seguimento. A verificação de nomenclatura do validador aceita
hífens (`CTRL-`, `MCH-`, `DEF-` ), e sua verificação de drivers avisa apenas em
expressões que precisam de Python, portanto, um rig de Mecanismos limpo não mostra validação
erros — apenas aquele que avisa sobre o osso `root` descrito em Limites desta versão.

## Show Helpers (mostrar ajudas)

**Show Helpers** é uma preferência para todos os BoneCraft:**Preferências →
Complementos → BoneCraft → Ajudantes**. Off esconde o texto didático em todos os lugares: o quê/quando
linhas, as notas **How this works** e as frases completas de etapas guiadas (aquelas
tornam-se rótulos curtos). As próprias etapas, as listas, testes, avisos e
As dicas de ferramentas instantâneas de Blender sempre permanecem.

O botão VRChat **Compact Mode** é seu atalho: Modo Compacto ativado significa Mostrar
Ajudantes desligados.

## Limites desta versão

- Os mecanismos Click Turn, Track e Linkage vêm depois.
- A exportação do mecanismo do movimento do mecanismo cozido ocorre mais tarde, após a mão da área de trabalho
verifique. Até então, os ossos `DEF-` são os ossos a serem exportados.
- BoneCraft não detecta colisões. Use o teste e veja.
- Um Gear Link de giro livre segue apenas alças e engrenagens.
- O osso `root` da rig não está em nenhuma coleção de ossos, então o validador da rig
verificação de coleções avisa sobre isso e o quadro de tarefas mostra "Validação de plataforma
avisos (1)".

Próximo: [Ferramentas VRChat](08-vrchat.md)
