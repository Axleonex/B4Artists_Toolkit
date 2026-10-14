# Mechanisms (mecanismos)

[← Sumário](index.md)

## O que o Mechanisms faz

O Mechanisms transforma peças hard-surface em um rig mecânico que funciona: dobradiças, deslizadores, telescópios, pistões, engrenagens, seguidores e transformações inteiras tocadas por um único controle deslizante. Ele constrói ossos e restrições comuns do Blender, então você pode ver e mudar tudo o que ele cria, e o rig funciona no Blender sem scripts. As engines de jogo recebem os ossos `DEF-`. A exportação para engines do movimento com bake dos mecanismos virá depois (veja Limites desta versão).

O BoneCraft fornece as ferramentas, não uma arma. As peças, quem traz é você.

Palavras usadas nos painéis e nesta página:

| Palavra | Significado |
|---|---|
| *Peça* (Part) | Um item que se move como um bloco sólido: um objeto, ou um pedaço solto de uma malha. Uma peça pode ir montada sobre outra peça. |
| *Articulação* (Joint) | Como uma peça pode se mover: Hinge (gira), Slide (desliza), Telescope (estende segmentos encaixados). |
| *Ligação* (Link) | O que move uma peça por você: Piston, Gear Link, Follow. |
| *Alça* (Handle) | O osso que você arrasta na viewport. Cada articulação tem uma. O valor dela também é um controle deslizante no painel. |
| *Sequência* (Sequence) | Uma transformação tocada por um único controle deslizante, feita de etapas. |
| *Forma* (Form) | Um conjunto salvo de valores de alças e sequências, como "Stowed" (guardado) ou "Rifle" (fuzil). |

## Onde fica

- **Aba BoneCraft → Mechanisms** na viewport 3D. A aba BoneCraft fica na Tool Shelf da esquerda (pressione **T**), a menos que você a tenha movido para a barra lateral da direita (**N**) nas Preferências. Ela fica entre Skin e Revisão. Aparece quando uma malha está ativa (para começar um rig) ou quando uma armadura com mecanismos está ativa.
- Properties → Scene → Mechanisms. Os painéis Cena aparecem quando Preferences → Tabs → Scene Properties → Show está ativado. Ocultar uma aba da viewport não oculta essa cópia.

Dentro do Mechanisms há quatro subseções: **1. Parts** (peças), **2. Joints & Links** (articulações e ligações), **3. Sequences** (sequências) e **4. Controls** (controles). Elas aparecem assim que o rig tem peças. Antes disso você só vê **Add Parts from Selection** (adicionar peças da seleção).

Cada botão é um passo de desfazer. Se uma construção falhar, tudo o que ela mudou é desfeito e o painel mostra o motivo.

## Peças

1. Selecione os objetos das peças (ou uma malha feita de pedaços soltos) no Modo Objeto.
2. Clique em **Add Parts from Selection**.
   - Vários objetos: uma peça por objeto. Cada objeto fica com o osso da sua peça como pai e permanece onde está.
   - Uma malha com pedaços soltos: uma peça por pedaço. Cada pedaço recebe um grupo de vértices para o seu osso e a malha recebe um modificador Armadura.
   - Na primeira vez, o BoneCraft cria o rig (uma armadura) para você.
3. Selecione uma peça na lista para editá-la.

Para cada peça:

- **Rides on:** (montada em): escolha a peça com a qual esta se move. Uma peça filha segue a peça pai. "the rig" significa que ela vai montada na raiz do rig.
- **Size** (tamanho) define o comprimento do osso, que define o tamanho da alça.
- **Edit Pivot** (editar pivô) coloca um marcador na peça. Arraste-o até onde a peça deve girar ou deslizar e clique em **Apply Pivot** (aplicar pivô). Os ossos da peça vão para lá e o objeto fica no lugar.
- **Apply Transforms** (aplicar transformações) aparece quando uma peça de objeto tem rotação ou escala não aplicada. Clique nele. Transformações não aplicadas inclinam os eixos.
- O botão **X** remove a peça. Ele se recusa enquanto uma articulação, uma ligação ou outra peça a usar, e as nomeia.
- **Merge for VRChat** (mesclar para VRChat; duas ou mais peças de objeto) une as peças de objeto em uma malha, com um grupo de vértices por objeto anterior e um modificador Armadura. Faça isso por último. As peças unidas viram pedaços soltos dessa malha. Ele remove cada grupo de vértices com o nome de um osso desta armadura (exceto o osso `DEF-` da própria peça), então mescle só peças que tenham rig apenas com o rig de mecanismos.

Você pode renomear o objeto de uma peça: as peças são marcadas nos seus objetos, então a peça encontra seu objeto de novo. Uma cópia do objeto (Shift+D) não fica com a peça. Se o objeto de uma peça for excluído, a peça mostra "Part '<name>' is missing" (a peça '<name>' está faltando) com **Reassign** (reatribuir) e **Excluir**. Os outros mecanismos continuam funcionando.

- **Reassign** usa a malha que você selecionou. Ele recusa o que não é malha e recusa um objeto que outra peça de objeto já usa. Pedaços soltos de uma mesma malha podem compartilhar essa malha.
- **Excluir** remove a peça (veja Edições e mudanças à mão, abaixo, para quando isso é recusado).

## Articulações e ligações, um exemplo de cada

Adicione uma articulação com **Add Joint** (adicionar articulação) e uma ligação com **Add Link** (adicionar ligação). Cada escolha inicia uma construção guiada. Elas funcionam pela aba da viewport e pela aba Cena do editor de Propriedades; pela aba Cena, o guia usa a maior viewport 3D da tela. Regras curtas para toda construção guiada:

- Clique nas peças na viewport. As peças clicadas ganham um contorno e um número.
- Quando um passo precisa de um eixo, pressione **X**, **Y** ou **Z**, ou **A** para alinhar com a seleção. **Align to Selection** (alinhar com a seleção) serve para dobradiças inclinadas. Ele precisa que a malha da peça ainda esteja no Modo Edição com uma aresta ou face selecionada quando você pressiona **A**, e o guia ignora **Tab**. Então entre primeiro no Modo Edição na malha da peça e selecione uma aresta ou face. Continue no Modo Edição, inicie **Add Joint → Hinge**, clique na peça e pressione **A**. Se nada utilizável estiver selecionado, o guia avisa e você pode pressionar outra tecla.
- O último passo pré-visualiza o mecanismo se movendo em loop. **Enter** o mantém. **Esc** o remove.
- O cabeçalho e a barra de status mostram uma frase completa em cada passo. Com Show Helpers (mostrar ajudas) desativado, mostram um rótulo curto.

Cada linha da lista Joints & Links tem quatro botões de ícone: **Test** (triângulo de reprodução), **Editar** (lápis, mostra as configurações), **Detach** (desanexar; corrente quebrada) e **Excluir** (X).

Depois da construção, o item selecionado na lista mostra só as configurações que o tipo dele usa.

### Hinge (dobradiça)

Hinge de lâmina, 0°…90°:

1. Add Parts from Selection com uma peça Blade (lâmina).
2. **Add Joint → Hinge**. Clique em Blade. Pressione **X**. Pressione **Enter**.
3. Você obtém uma alça em semicírculo, `CTRL-Blade`, e uma *Blade Hinge* na lista. Defina **Min** como 0 e **Max** como 90 (em ° para uma Hinge).
4. Teste: arraste a alça em semicírculo. Ela para em 90°. **Set Min** (definir mín.) e **Set Max** (definir máx.) copiam a pose atual da alça para os limites.

Um limite menor que uma volta completa precisa ficar dentro de −180°…180°. Limites como 170°…190° são recusados com uma mensagem. Uma faixa de uma volta completa ou mais (por exemplo −180°…180°) gira livremente, sem limite.

### Slide (deslizador)

Slide de cano, 0…0.3:

1. **Add Joint → Slide**. Clique na peça Barrel (cano). Pressione **Y**. Pressione **Enter**.
2. Você obtém uma alça em seta. Defina **Min** como 0 e **Max** como 0.3 (unidades da cena).
3. Teste: arraste a seta. O cano desliza e para em 0.3.

### Telescope (telescópio)

Mastro com três segmentos:

1. Crie a base e três peças de segmento.
2. **Add Joint → Telescope**. Clique na base. Clique em cada segmento, da base para fora. Pressione **Enter**. Pressione a tecla do eixo. Pressione **Enter** para manter.
3. Você obtém uma alça em seta na base. **Length** (comprimento) é o curso total; **Shares (empty = even)** (partes; vazio = iguais) o divide entre os segmentos. Para testar partes personalizadas, defina primeiro **Length** como 1 e digite `0.5, 0.25, 0.25`. As partes precisam somar a Length, para que a ponta percorra o comprimento inteiro. Um erro de digitação (por exemplo `0.5, abc`) é recusado com a mesma mensagem simples: as partes precisam ser números, um por segmento, que somem a Length.
4. Teste: arraste a única seta. Os três segmentos se estendem conforme suas partes. **Set Max** define a Length a partir da pose da alça.

### Piston (pistão)

Elevador: cilindro na estrutura, haste no braço.

1. Dê primeiro uma Hinge ao braço e faça o braço ir montado na estrutura.
2. **Add Link → Piston**. Clique na peça do cilindro (na estrutura). Clique na peça da haste (no braço).
3. Você obtém um Piston sem alça. Cada peça aponta para o ponto de fixação da outra. **Esticar** (opcional) estica a haste, para molas e cabos.
4. Teste: mova a alça do braço. O pistão acompanha. Se nada move o Piston ainda, a construção funciona, mas sem pré-visualização, e **Test** avisa.

### Gear Link (ligação de engrenagem)

Engrenagem 20:40:

1. As duas peças precisam antes de uma articulação. A peça motora precisa de uma Hinge. Para Gear e Belt, a peça movida precisa de uma Hinge; para Rack, de uma Slide.
2. **Add Link → Gear Link**. Clique na peça motora. Clique na peça movida.
3. Nas configurações dela, defina **Source Teeth** (dentes da origem) como 20 e **Target Teeth** (dentes do destino) como 40 (ou digite um **Ratio**). **Kind** (tipo) é Gear, Belt ou Rack. **Reverse** (inverter) inverte o sentido.
4. Teste: gire a origem. Com **Kind** em Gear, o destino gira −0.5× o tanto (+0.5× com Belt). Um Gear inverte o sentido, um Belt o mantém e um Rack transforma rotação em deslizamento (distância por radiano = **Ratio** × **Pinion Radius** (raio do pinhão)).

Como o BoneCraft o constrói depende da faixa da Hinge de origem:

- Menos de uma volta completa: uma restrição Transformação. Ela segue tudo o que move a origem, inclusive sequências.
- Uma volta completa ou mais: um driver que não precisa de Python. O destino gira sem parar com a origem. Ele segue só alças e engrenagens. O Validador de Rig avisa quando uma sequência ou um Follow seria perdido.

### Follow (seguidor)

Blade 0–90° levanta Cover (tampa) 0–40°:

1. As duas peças precisam de uma Hinge ou de uma Slide. Uma Hinge de origem precisa de limites menores que uma volta completa; uma origem que gira livremente é recusada.
2. **Add Link → Follow**. Clique na peça que lidera (Blade). Clique na peça que segue (Cover).
3. As faixas começam como a faixa completa de cada articulação. Defina **Source Range** (faixa de origem) como 0…90 e **Target Range** (faixa de destino) como 0…40. Além de qualquer uma das pontas, o destino fica parado.
4. Teste: mova a alça de Blade. Cover acompanha.
5. Marque **Curve** (curva) para remodelar a correspondência no editor de gráficos. O BoneCraft nunca sobrescreve sua curva (veja Edições e mudanças à mão, abaixo).

### Sequence (sequência)

Capture Step para dobrar uma arma:

1. Em **3. Sequences**, clique em **Add Sequence** (adicionar sequência). Isso cria uma alça de controle deslizante `CTRL-SEQ-<name>`.
2. Clique em **Capture Step** (capturar etapa). O controle deslizante salta para o fim (1).
3. Faça a pose das alças das articulações para a primeira etapa. Clique em **Capture Step** de novo. Cada alça que se moveu vira uma etapa com seu valor alvo, e as alças voltam a zero.
4. Repita o passo 3 para mais etapas. Cada etapa nova ocupa por padrão o próximo quarto do controle deslizante.
5. Defina o **Alvo**, a suavização (Linear, Ease In, Ease Out, Ease In Out, Snap), **Iniciar** e **End** (fim) de cada etapa. Fora do seu trecho, uma etapa mantém o valor final. Várias sequências podem se empilhar.
6. Clique em **Test**: o controle deslizante toca 0 → 1 → 0.

Ao lado de **Capture Step** e **Test**, a sequência selecionada tem **Detach** (corrente quebrada) e **Excluir** (X). Uma sequência retida (por exemplo uma etapa cuja curva você remodelou) mostra sua mensagem e um botão **Restaurar**. Restaurar regenera as etapas a partir do registro. Keep mine (manter o meu) não é oferecido para uma sequência.

## Test

**Test** (o botão de reprodução na lista, e em 3. Sequences) percorre um mecanismo por toda a sua faixa, ida e volta. Ele não grava chaves e restaura a pose ao terminar. Pressione **Esc** para pará-lo antes; a pose também é restaurada nesse caso. Em um Gear Link ou Follow, ele percorre a origem. Em um Piston, percorre a articulação que o move. Fique de olho em peças que colidem; o BoneCraft não detecta colisões.

## Formas

Em **4. Controls**:

- Cada articulação e cada sequência tem um controle deslizante. Ele é o próprio canal da alça, então arrastar a alça e usar o controle deslizante são a mesma coisa.
- **Save Form** (salvar forma) salva com um nome o valor de cada alça e de cada controle deslizante de sequência. Renomeie-a na lista.
- **Go to Form** (ir para a forma) coloca cada controle nos valores salvos.
- **Go and Key** (ir e inserir chave) faz o mesmo e ainda insere chaves no quadro atual.
- O **X** ao lado da lista remove uma forma.

## O que o BoneCraft constrói

Para cada peça:

| Osso | Função | Visível |
|---|---|---|
| `CTRL-<part>` | A alça. O valor dela é o controle deslizante do painel. Só Hinge, Slide e Telescope a criam. | Sim |
| `MCH-<part>` | Soma a alça e cada ligação e depois aplica os limites. | Oculto |
| `DEF-<part>` | Copia `MCH-<part>`. A malha fica vinculada a ele. As engines recebem este osso. | Oculto |

Os ossos ficam nas coleções `Mechanism Controls`, `Mechanism MCH` e `Mechanism DEF`. Uma peça sem articulação tem só ossos `MCH-` e `DEF-`. A alça de um Telescope é `CTRL-<telescope name>`. A de uma sequência é `CTRL-SEQ-<name>`. Um Piston adiciona ossos `MCH-<part>-aim` e `MCH-<part>-target` para cada uma das suas duas peças.

As restrições de `MCH-<part>` vêm sempre na mesma ordem: Copiar transformações da alça, depois a contribuição de cada ligação, depois o Limite de rotação ou o Limite de posição da articulação. `DEF-<part>` tem uma Copiar transformações de `MCH-<part>`.

Tudo o que o BoneCraft constrói é marcado com o seu registro: os nomes das restrições começam com `BC·<id>·<role>`, e os ossos levam as propriedades `bc_mech_id` e `bc_mech_role`. O BoneCraft encontra seus ossos pela marca, não pelo nome, então você pode renomear qualquer osso. Uma reconstrução o encontra de novo e não cria duplicado.

Com Show Helpers ativado, cada articulação e cada ligação tem uma nota **How this works** (como funciona). Ela lista as restrições pelo nome, diz o que cada uma faz e tem um botão **Selecionar** (ícone de seta) para inspecionar o osso.

Suas próprias restrições, drivers e ossos nunca são tocados. Uma restrição que você adiciona a um osso MCH fica abaixo das do BoneCraft depois de uma reconstrução.

## Edições e mudanças à mão

- As **Value edits** (edições de valores: limites, ratio, faixas, tempos, suavização, aparência da alça) atualizam as restrições existentes no lugar. Não há reconstrução.
- As **Structural edits** (edições de estrutura: o **Kind** de um Gear Link, a **Curve** de um Follow, o **Esticar** de um Piston) substituem as restrições desse mecanismo e reconstroem só ele.
- **Changed by hand.** (mudado à mão) Se você editar uma restrição do BoneCraft (por exemplo um Limite), a mensagem do mecanismo termina com "(changed by hand)". O BoneCraft nunca a sobrescreve em silêncio. Escolha:
  - **Keep mine** (manter o meu) copia seus valores para o registro. Ele recusa o que não consegue ler de volta e diz para usar Restaurar ou Detach.
  - **Restaurar** descarta sua edição e reconstrói a partir do registro.
- Um mecanismo retido também retém cada mecanismo que usa os ossos dele, até você resolver.
- Uma curva remodelada funciona igual. Se você remodelar a curva de um Follow (**Curve** marcada) no editor de gráficos e depois mudar um valor que a substituiria, como a Target Range, a mensagem do Follow termina com "(changed by hand)". **Keep mine** mantém sua curva. **Restaurar** a regenera.
- Uma sequência retida mostra sua mensagem e **Restaurar** em **3. Sequences**, com **Detach** e **Excluir** ao lado. Keep mine não é oferecido para sequências.
- **Detach** (botão de corrente quebrada) apaga o registro e as marcas, mas mantém os ossos e as restrições como seu próprio rig feito à mão. Detach e Excluir recusam um registro que outro registro usa, e nomeiam quem o usa.
- **Excluir** (botão X) remove o registro e tudo o que o BoneCraft construiu para ele.
- Um loop de ligações é recusado antes de qualquer construção, e o loop é nomeado, por exemplo "Blade Hinge → Cover Follow → Blade Hinge would loop." (formaria um loop)

O Validador de Rig e o Quadro de Tarefas informam loops de ligações, peças faltando, ossos DEF movidos de fora do seu mecanismo, drivers que precisam de Python e Gear Links que perdem uma sequência ou um Follow. A verificação de nomes do validador aceita hífens (`CTRL-`, `MCH-`, `DEF-`), e a verificação de drivers só avisa em expressões que precisam de Python, então um rig de Mechanisms limpo não mostra erros de validação: só o aviso único sobre o osso `root` descrito em Limites desta versão.

## Show Helpers (mostrar ajudas)

**Show Helpers** é uma única preferência para todo o BoneCraft: **Preferências → Add-ons → BoneCraft → Helpers**. Desativada, ela oculta em todo lugar o texto didático: as linhas o quê / quando, as notas **How this works** e as frases completas dos passos guiados (que viram rótulos curtos). Os passos em si, as listas, Test, os avisos e as dicas de passar o mouse do Blender sempre ficam.

O botão **Modo Compacto** do VRChat é o atalho dela: Modo Compacto ativado significa Show Helpers desativado.

## Limites desta versão

- Os mecanismos Click Turn, Track e Linkage virão depois.
- A exportação para engines do movimento com bake dos mecanismos virá depois, após a verificação manual no desktop. Até lá, os ossos `DEF-` são os ossos a exportar.
- O BoneCraft não detecta colisões. Use Test e observe.
- Um Gear Link que gira livremente segue só alças e engrenagens.
- O osso `root` do rig não está em nenhuma coleção de ossos, então a verificação de coleções do Validador de Rig avisa sobre ele e o Quadro de Tarefas mostra "Rig validation warnings (1)" (avisos de validação do rig (1)).

Próximo: [Ferramentas do VRChat](08-vrchat.md)
