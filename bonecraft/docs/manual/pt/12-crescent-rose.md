# Tutorial: Crescent Rose com mecanismos

[← Conteúdo](index.md)

<style>
section.chapter:has(#ch-12-crescent-rose) img {max-width:100%;width:auto;height:auto;}
img.manual-image-70 {max-height:70mm;}
img.manual-image-100 {max-height:100mm;}
img.manual-image-110 {max-height:110mm;}
img.manual-image-115 {max-height:115mm;}
img.manual-image-135 {max-height:135mm;}
img.manual-image-155 {max-height:155mm;}

@media print {
  h3[id^="12-crescent-rose--"] { break-before: page; break-after: avoid; }
  h2:has(+ h3[id^="12-crescent-rose--"]) { break-before: page; break-after: avoid; }
  h2 + h3[id^="12-crescent-rose--"] { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) { break-after: avoid; }
  section.chapter:has(#ch-12-crescent-rose) p:has(> img) + p { break-before: avoid; }
  section.chapter:has(#ch-12-crescent-rose) table { break-inside: avoid; }
  [id="12-crescent-rose--o-que-você-construiu"] { break-before: page; break-after: avoid; }
}
</style>

## O que você vai construir

Crescent Rose é a foice que também é um rifle. Neste tutorial você equipa um modelo com mecanismos, de modo que um controle deslizante transforme a foice em um rifle e um segundo controle deslizante dobre o rifle em sua forma compacta. No caminho você usa todos os mecanismos de articulação e elo que existem hoje, exceto o Gear Link: oito dobradiças, três corrediças, um telescópio, um pistão e um seguimento, depois duas sequências e três formas.

Os formulários ensinam poses para este modelo feito em leque. Os mecanismos não detectam colisões nem fazem uma réplica fisicamente projetada: inspecione as folgas ao adaptar a rig.

O resultado é o arquivo `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Abra-o a qualquer momento para comparar.

## Antes de começar

- Os arquivos: `examples/crescent-rose/CrescentRose_parts.blend` é o modelo já dividido em 15 objetos-partes; comece o tutorial a partir dele. `CrescentRose_Mechanisms.blend` é o rig acabado.
- Tempo: permita uma sessão separada para preparação do FBX e outra para a aula de Mecanismos; estes são exercícios substanciais, não corridas de velocidade cronometradas. Salve pontos de verificação entre os estágios.
- Palavras: leia primeiro "O que o mecanismo faz" em [Mecanismos](07-mechanisms.md): define peça, junta, link, alça, sequência e forma.
- Idioma: as capturas de tela mostram Bforartists em inglês com os painéis de BoneCraft em inglês. Os próprios painéis do BoneCraft seguem a configuração **Language** em suas preferências; o resto do Bforartists segue a linguagem de interface do Bforartists. Se o seu Bforartists estiver em um idioma que BoneCraft não traduz, seus painéis permanecerão em inglês e esta edição ainda será aplicada.
- Rota inicial: use P1-P8 abaixo para o FBX original ou pule para a Etapa 1 com o arquivo preparado. Ambas as rotas usam as mesmas 15 peças.
- Versão: instruções e capturas de interface genuínas foram verificadas com BoneCraft `9.1.2` em Bforartists `5.2.0`, usando seu mapa de teclado padrão.

Marcas numeradas em vermelho identificam o que clicar, digitar ou inspecionar. Siga a tecla de ação numerada de cada imagem em ordem (1, depois 2 e depois 3). Os números são reiniciados em cada imagem. Um resultado em caixa é uma verificação; uma parte ou botão circulado é o alvo da interação.

## Prepare o FBX original (P1-P8)

Pule esta seção se estiver usando `CrescentRose_parts.blend`. Trabalhe em um novo arquivo e mantenha a fonte FBX e sua pasta `CrescentRoseTextures` juntas. Essas etapas foram repetidas em Bforartists 5.2.0 com o mapa de teclado padrão. Use o menu do modo visível: a guia pode alternar as sobreposições neste mapa de teclado em vez de entrar no modo de edição.

### P1 - Importe o FBX

Comece com uma cena vazia. Escolha **File > Import > FBX (.fbx) (Legacy)**, selecione `CrescentRose.fbx` e deixe a escala de importação em `1.00`. Use o importador Legacy para esta receita. O Outliner contém uma raiz e três malhas de material: `Black01`, `Blades01` e `Red01`. Pressione Numpad 3 para visualização direita e Home para enquadrá-los.

![P1: Opções de importação herdadas do FBX com Escala 1.00](../images/crescent-rose/en/prep-01-import-fbx.png){.manual-image-155}

*1: Selecione CrescentRose.fbx. 2: Mantenha a escala em 1,00. 3: Clique em Importar FBX; use o importador legado.*

### P2 - Preservar o posicionamento e definir o tamanho

No Modo Objeto selecione as três malhas. Use **Object > Parent > Clear and Keep Transformation**. Remova a raiz agora não utilizada da sua cena de trabalho. Com todas as três malhas selecionadas, use**Object > Apply > Rotation & Scale**. A arma importada tem aproximadamente `0.32 m` de altura. Dimensione todos os três juntos por `6.25` (neste mapa de teclado Bforartists, Ctrl+R inicia Escala; digite 6.25 e confirme) e, em seguida, aplique Rotação e Escala novamente. A arma completa agora tem aproximadamente `1.997 m` de altura. Faça isso uma vez; o atalho preparado já está dimensionado.

![P2: parentalidade clara, preservando a colocação](../images/crescent-rose/en/prep-02-unparent-command.png){.manual-image-135}

*1: Pressione F3 e pesquise Clear Parent Keep Transform. 2: Escolha Limpar e Manter a Transformação. Repita para todas as três malhas antes de remover a raiz.*

![P2: rotação e escala aplicadas na arma importada](../images/crescent-rose/en/prep-02-scale.png){.manual-image-115}

*1: Depois de dimensionar as três malhas juntas em 6,25, aplique Rotação e Escala; A rotação deve ser 0. 2: A escala deve ser 1 em todos os eixos.*

O campo Dimensões de um objeto individual mede apenas aquela malha de material. Verifique a extensão combinada de baixo para cima ao medir a arma. Todos os três objetos devem apresentar rotação zero e escala 1 antes da separação.

### P3 - Conecte os materiais

Mude para a área de trabalho Sombreamento e Visualização de material. Para cada um dos três materiais, carregue suas imagens `BaseColor`, `Metallic`, `Roughness` e `Normal` correspondentes de `CrescentRoseTextures`. Conecte a cor da textura da imagem à entrada Principled BSDF correspondente. BaseColor usa **sRGB**; Metálico, Rugosidade e Uso normal `Non-Color`. Para Normal, insira um nó**Normal Map**, mantenha `Tangent Space`, conecte a Cor da imagem à sua Cor e conecte sua saída Normal ao Princípio BSDF Normal. Mantenha os UVs existentes.

![P3: quatro mapas de textura e mapa normal do espaço tangente conectados para o material preto](../images/crescent-rose/en/prep-03-materials.png){.manual-image-155}

*1: Conecte a Cor BaseColor à Cor Base BSDF. 2: Mantenha BaseColor em sRGB. 3: Defina todos os mapas de dados como Não Coloridos. 4: Conecte imagem Normal > Mapa Normal > BSDF Normal, usando Espaço Tangente.*

![P3: todos os três materiais no Material Preview](../images/crescent-rose/en/prep-03-shaded.png){.manual-image-155}

*1: Verifique o material da lâmina. 2: Verifique os materiais do corpo vermelho/preto no Material Preview; sem texturas rosa faltando.*

Repita as mesmas conexões para a lâmina e os materiais vermelhos. Verifique o espaço de cores de cada imagem após escolhê-la; a configuração pertence à imagem. A arma deve ser vermelha, preta e metálica, sem falta de texturas rosa.

### P4 - Separe as peças soltas

Selecione todas as três malhas de material, escolha **Edit Mode** no menu do modo viewport, selecione toda a geometria e use**Mesh > Separate > By Loose Parts**. Retorne ao modo de objeto. Existem**37** objetos de malha neste momento. Os sufixos numéricos gerados podem variar, portanto identifique-os por posição e formato.

![P4: entre no modo de edição e escolha Por peças soltas](../images/crescent-rose/en/prep-04-separate-command.png){.manual-image-135}

*1: Mude para o Modo de Edição e selecione toda a geometria. 2: Pressione F3, pesquise Separar Solto e escolha Por Peças Soltas.*

![P4: as 37 peças soltas após a separação](../images/crescent-rose/en/prep-04-separate.png){.manual-image-155}

*1: Verifique se o total de objetos é 37 após a separação. 2: Use o Outliner para selecionar peças por formato e localização; os sufixos podem variar.*

### P5 – Junte-se aos 15 grupos em movimento

Selecione as peças que devem se mover juntas e use **Object > Join** (Ctrl+J). Renomeie o objeto resultante no Outliner. Para peças emparelhadas em lados opostos, orbite a vista para selecionar ambas; verifique a seleção antes de ingressar. Trabalhe da ponta da lâmina para dentro, depois do receptor e da haste. A tabela lista todas as ilhas de origem; um nome de material descreve sua aparência, não o nome final do objeto.

|Objeto final|Peças para combinar|Vértices de malha após a união|
|---|---|---:|
|`BladeTip` |Botão de junta de ponta preto e ponta de metal|252|
|`Blade2` |Duas placas metálicas do segundo segmento e duas tampas vermelhas|1000|
|`Blade1` |Duas placas metálicas do primeiro segmento mais próximas da cabeça|512|
|`HeadMount` |Bloco traseiro, tampa superior e núcleo pretos; duas placas internas vermelhas e duas tampas superiores finas|1395|
|`PlateL` |Uma placa externa vermelha em X negativo|676|
|`PlateR` |Uma placa frontal externa vermelha em X positivo|676|
|`RearSpike` |Duas lâminas de metal, duas tampas de articulação vermelhas e duas placas de montagem vermelhas|1194|
|`Receiver` |Corpo preto e botão pequeno, anel de metal acima do parafuso, caixa longa vermelha|2609|
|`Grip` |Bloco de aderência vermelho abaixo do receptor|194|
|`Magazine` |Tubo preto abaixo do corpo|96|
|`Bolt` |Cilindro de parafuso vermelho e suas duas peças de botão|362|
|`Pole` |Eixo inferior de metal e colarinho vermelho|148|
|`ButtSpike` |Ponta inferior de metal|110|
|`StrutBase` |Haste vermelha fina entre o receptor e a cabeça|34|
|`StrutRod` |Manga preta entalhada em torno dessa haste|108|

Deve haver **15 malhas e 9.366 vértices** no total. Não junte as placas externas no Blade1 ou as duas peças do suporte. O suporte já possui duas peças separadas; nenhuma bissecção é necessária. A etapa 2 repete os nomes das peças finalizadas e seus pais posteriores.

![P5: todos os 15 grupos móveis nomeados no Outliner](../images/crescent-rose/en/prep-05-group-parts.png){.manual-image-155}

*1: Renomeie cada grupo unido no Outliner para corresponder aos 15 nomes na tabela.*

![P5: as duas placas de origem Blade1 selecionadas antes da união](../images/crescent-rose/en/prep-05-blade1.png){.manual-image-155}

*1: Selecione as duas placas metálicas Blade1 em lados opostos. 2: Verifique se ambos os objetos estão selecionados, então use Join e renomeie o resultado Blade1.*

![P5: Menu Objeto Comando Join](../images/crescent-rose/en/prep-05-join-command.png){.manual-image-135}

*1: Abra o Objeto após selecionar apenas as peças de um grupo. 2: Escolha Unir (Ctrl+J). Este corte de menu identifica o comando; use a seleção de duas peças mostrada acima.*

### P6 - Centralize as origens

No Modo Objeto selecione todas as 15 malhas. Escolha **Object > Set Origin > Origin to Geometry** e defina a opção Centro da operação como `Bounds Center`. Verifique a rotação zero e a escala 1. Os objetos ainda não têm pais e não há armadura. Estas são origens de preparação convenientes; A etapa 6 posteriormente move os pivôs do mecanismo para suas juntas reais.

![P6: Objeto > Definir Origem > Origem para Geometria](../images/crescent-rose/en/prep-06-origin-command.png){.manual-image-135}

*1: Objeto Aberto. 2: Passe o mouse sobre a origem do conjunto. 3: Escolha Origem para Geometria; defina Limites Center nas opções de operação.*

![P6: a origem Blade1 centralizada com transformações aplicadas](../images/crescent-rose/en/prep-06-origins.png){.manual-image-155}

*1: A origem laranja agora está centralizada na malha. 2: Confirmar rotação 0. 3: Confirmar escala 1. Os pivôs do mecanismo são movidos posteriormente.*

### P7 – Redimensionar e empacotar as texturas

No Editor de Imagens selecione cada um dos **12 mapas utilizados** (quatro por material). Escolha**Image > Resize**, defina largura e altura como**1024**, confirme e escolha**Image > Pack**. Repita para cada mapa usado. Compactar a imagem redimensionada preserva os pixels dentro da mistura; não substitua os JPEGs de origem. Verifique a visualização do material posteriormente.

![P7: Menu de imagem com textura redimensionada de 1024 por 1024](../images/crescent-rose/en/prep-07-pack-textures.png){.manual-image-155}

*1: Escolha Imagem > Redimensionar e insira 1024 para largura e altura. 2: Verifique as dimensões resultantes de 1024 x 1024. 3: Escolha Pacote. Repita para todos os 12 mapas usados.*

### P8 - Salve e reabra o arquivo preparado

Salve sua cópia de trabalho como `CrescentRose_parts.blend`. Abra-o novamente e verifique as 15 malhas nomeadas, suas transformações e os materiais vermelho/preto. Todos os 12 mapas devem permanecer disponíveis sem depender do diretório de textura original. Use a visualização direita e a página inicial novamente e continue com a Etapa 1.

![P8: o arquivo preparado foi reaberto com a arma texturizada intacta](../images/crescent-rose/en/prep-08-save-parts.png){.manual-image-155}

*1: Abra Arquivo para Salvar como e depois Abra para recarregar sua cópia de trabalho. 2: Confirme se as 15 malhas nomeadas sobreviveram. 3: Verifique os materiais; a barra de título identifica o arquivo reaberto.*

## A. Abra o arquivo

### Passo 1 — Abra o arquivo de peças

Abra `examples/crescent-rose/CrescentRose_parts.blend`. Mude a janela de visualização para o sombreamento Material Preview e pressione Numpad 3 para a visualização Right: a lâmina aponta para a esquerda, a ponta para baixo. Pressione Home para enquadrar a arma.

![Etapa 1: o arquivo de peças na vista direita](../images/crescent-rose/en/01-open-file.png){.manual-image-155}

*1: Clique em Visualização do material. 2: Pressione Numpad 3 até que a visualização diga Ortogonal Direita; pressione Home para enquadrar a arma.*

**O que você deveria estar vendo:** A foice em vermelho e preto, com cerca de 2 m de altura, sem nada selecionado.

### Passo 2 — Conheça as peças

O Outliner lista os 15 objetos. Cada um é uma peça que se move como um bloco:

|Objeto|O que é isso|Continua|
|---|---|---|
|`Receiver` |O corpo do rifle com mira, gatilho e mira|a rig|
|`Grip` |A aderência sob o receptor|`Receiver` |
|`Magazine` |O magazine de cilindros|`Receiver` |
|`Bolt` |O parafuso|`Receiver` |
|`Pole` |O eixo inferior e seu colar|`Receiver` |
|`ButtSpike` |O pico na parte inferior|`Pole` |
|`HeadMount` |O bloco da cabeça onde a lâmina está pendurada|`Receiver` |
|`Blade1` |O primeiro segmento da lâmina, mais próximo da cabeça|`HeadMount` |
|`Blade2` |O segundo segmento|`Blade1` |
|`BladeTip` |A dica|`Blade2` |
|`RearSpike` |O pico na parte de trás da cabeça|`HeadMount` |
|`PlateL`, `PlateR` |As placas laterais externas da cabeça|`HeadMount` |
|`StrutBase` |A haste fina entre o receptor e a cabeça|`Receiver` |
|`StrutRod` |A manga entalhada em torno daquela haste|`HeadMount` |

![Passo 2: os 15 objetos de parte no Outliner](../images/crescent-rose/en/02-the-parts.png){.manual-image-155}

*1: Identifique os três segmentos da lâmina. 2: Combine os nomes do corpo, cabeça e poste com a tabela. 3: Mantenha StrutBase e StrutRod como objetos separados.*

Para o FBX original, siga P1-P8 acima. O arquivo preparado fornecido foi criado por meio dessas ações de interface; o script de preparação do repositório fornece uma tabela de agrupamento de referência.

### Passo 3 — Encontre Mecanismos

Abra a guia BoneCraft na prateleira de ferramentas esquerda (se estiver oculta, pressione T sobre a janela de visualização e escolha Ferramentas no menu Alternar região) e expanda **Mechanisms**. Amplie a prateleira arrastando sua borda direita até que o texto do painel tenha espaço. Como alternativa, a mesma seção Mecanismos está disponível em**Properties > Scene** quando Propriedades da cena está definida como Mostrar nas preferências de BoneCraft. As capturas de tela usam a estante de ferramentas. Com uma malha ativa e sem rig ainda, encontre**Add Parts from Selection** no topo da seção. Selecione todas as peças no Passo 4 antes de clicar; as subseções numeradas tornam-se utilizáveis após a adição de peças.

![Etapa 3: a seção Mecanismos da guia BoneCraft](../images/crescent-rose/en/03-mechanisms-section.png){.manual-image-155}

*1: Clique na guia BoneCraft. 2: Expanda Mecanismos. 3: Encontre Adicionar peças da seleção; selecione as malhas antes de usá-las.*

## B. Peças

### Passo 4 — Adicionar peças da seleção

Passe o mouse sobre a viewport e pressione A para selecionar todos os 15 objetos. Clique em **Add Parts from Selection**.

![Etapa 4: todas as peças selecionadas, Adicionar peças da seleção](../images/crescent-rose/en/04-add-parts.png){.manual-image-155}

*1: Passe o mouse sobre a viewport e pressione A para selecionar as 15 malhas. 2: Clique em Adicionar peças da seleção.*

**O que você deveria ver:** Uma nova armadura, "Mechanism Rig", aparece no Outliner com as peças abaixo dela. Os objetos de malha permanecem selecionados após a operação.**1. Parts** lista as 15 partes, e a guia BoneCraft agora começa com a visão geral do rig, que você pode recolher.

### Passo 5 – Continuação

Uma peça monta na parte à qual está fixada. Clique em `Blade1` na lista **1. Parts**, abra o menu "Passeios em" na lista e escolha `HeadMount`. Faça o mesmo para todas as peças da tabela da etapa 2. `Receiver` mantém "o rig".

![Etapa 5: Blade1 anda no HeadMount](../images/crescent-rose/en/05-rides-on.png){.manual-image-155}

*1: Selecione Blade1 na lista de peças. 2: Abra Rides on e escolha HeadMount. Repita usando a tabela pai.*

### Passo 6 — Pivôs

Uma dobradiça gira em torno do pivô de sua peça. Os segmentos da lâmina, a cabeça e o punho devem girar nas articulações e não no centro. Com `Blade1` selecionado na lista, clique em **Edit Pivot**, selecione o marcador, pressione Ctrl+W para Mover em Bforartists, clique onde o segmento encontra a cabeça e clique em**Apply Pivot**. Trabalhe na vista lateral ortográfica para que a posição do pivô lateral permaneça inalterada. Repita para `Blade2` (onde encontra `Blade1` ), `BladeTip` (onde encontra `Blade2` ), `HeadMount` (seu ponto mais baixo, onde o suporte o encontra), `Grip` (sua borda superior), `RearSpike` (onde encontra a cabeça), `PlateL` e `PlateR` (o centro do parafuso redondo onde Blade1 encontra a cabeça), `StrutBase` (sua parte inferior) e `StrutRod` (sua parte superior). A posição do marcador na captura de tela é um guia; alguns milímetros não fazem diferença visível.

![Etapa 6: selecione a peça e clique em Editar pivô](../images/crescent-rose/en/06-edit-pivot-button.png){.manual-image-135}

*1: Selecione Blade1 em Peças. 2: Clique em Editar pivô; em seguida, mova e aplique o marcador conforme mostrado a seguir.*

![Etapa 6: marcador de pivô do Blade1 na junta, aplicar pivô](../images/crescent-rose/en/06-edit-pivot.png){.manual-image-155}

*1: Mova o marcador de pivô para a junta da lâmina com Ctrl+W. 2: Clique em Aplicar pivô para manter esse local.*

## C. A cabeça

### Passo 7 — Adicionar junta → Dobradiça

Abra **Add Joint → Hinge**. Uma compilação guiada é iniciada: o cabeçalho e a barra de status informam o que fazer em cada etapa.

![Etapa 7: menu Adicionar junta, dobradiça](../images/crescent-rose/en/07-head-hinge.png){.manual-image-155}

*1: Abra Adicionar junta. 2: Clique em Dobradiça. A construção guiada agora aguarda uma peça.*

### Passo 8 – Clique na cabeça

O cabeçalho diz "clique na parte que gira". Na vista Direita, a placa externa fica na frente da cabeça, então clique no bloco traseiro da cabeça, atrás das placas (o círculo). Se o cabeçalho tiver o nome `PlateR`, pressione Esc, reinicie **Add Joint > Hinge** e clique mais atrás. Se precisar ocultar uma obstrução, faça-o antes de iniciar o guia. O guia consome atalhos de teclado comuns enquanto está ativo.

![Etapa 8: clique no bloco traseiro da cabeça](../images/crescent-rose/en/08-head-hinge-click.png){.manual-image-155}

*1: Clique no bloco preto traseiro do HeadMount, atrás da placa externa vermelha. Verifique os nomes dos guias HeadMount.*

### Passo 9 — Pressione X e depois Enter

O cabeçalho agora pede o eixo. Pressione X: a cabeça gira em torno do eixo lateral e a guia visualiza o movimento em um loop. Pressione Enter para mantê-lo.

![Etapa 9: a etapa do eixo](../images/crescent-rose/en/09-head-hinge-axis.png){.manual-image-155}

*1: Siga o prompt do eixo: pressione X e depois Enter. 2: Observe a cabeça girar em torno de seu pivô antes de confirmar.*

**O que você deveria ver:** `HeadMount Hinge` na lista**2. Joints & Links** e seu controle deslizante em**4. Controls**. Use esses controles deslizantes no modo de objeto. Para usar as alças ósseas da viewport, selecione a armadura e alterne para o modo Pose.

### Passo 10 — Limites

Com `HeadMount Hinge` selecionado na lista, defina **Min** como 0 e**Max** como 120. Valores positivos viram a cabeça para baixo e para trás. Mantenha o limite de deslocamento de 120 graus; a sequência do rifle usará um alvo de 90 graus junto com as dobradiças da lâmina.

![Etapa 10: Mín. 0, Máx. 120](../images/crescent-rose/en/10-head-hinge-limits.png){.manual-image-155}

*1: Selecione Dobradiça HeadMount. 2: Defina Mín como 0. 3: Defina Máx como 120; clique duas vezes no número, digite e pressione Enter.*

### Passo 11 — Teste

Clique no botão de reprodução da linha. A cabeça se move para 120° e para trás, e a postura é restaurada.

![Etapa 11: teste na linha da dobradiça](../images/crescent-rose/en/11-test-head.png){.manual-image-155}

*1: Clique no pequeno triângulo de jogo na linha HeadMount Hinge. Observe a varredura e retorne.*

## D. A corrente da lâmina

### Passo 12 — Mais três dobradiças

Repita as etapas 7 a 10 para `Blade1`, `Blade2` e `BladeTip`: **Add Joint → Hinge**, clique no segmento, X, Enter e, em seguida,**Max** 120. Cada segmento passa pelo anterior, de modo que as três dobradiças formem uma corrente.

![Etapa 12: as três dobradiças do segmento da lâmina e a dobradiça da cabeça separada na lista](../images/crescent-rose/en/12-blade-hinges.png){.manual-image-155}

*1: Crie e selecione cada dobradiça de lâmina: Blade1, Blade2, BladeTip. 2: Defina Max como 120 para cada; use X como seu eixo.*

### Passo 13 — Experimente a corrente

Recolha **2. Joints & Links** para liberar espaço e expandir**4. Controls**. No modo de objeto, defina `Blade1 Hinge`, `Blade2 Hinge` e `BladeTip Hinge` para 60 graus, um de cada vez. Clique duas vezes em um campo numérico, pressione Ctrl+A, digite o valor e pressione Enter. Os segmentos posteriores se movem com os anteriores e a corrente se enrola. Defina todos os três valores de volta para 0 antes de continuar.

![Etapa 13: as três lâminas giram em 60 graus nos Controles](../images/crescent-rose/en/13-blade-chain.png){.manual-image-155}

*1: Insira 60 em cada um dos três controles deslizantes de lâmina. 2: Verifique os cachos da corrente juntos. Retorne todos os três controles deslizantes para 0.*

## E. Placas e suporte

### Passo 14 — Dobradiças nas placas

Adicione uma dobradiça em `PlateR` da mesma maneira, **Max** 30. `PlateL` está escondido atrás da cabeça na visualização direita: pressione Ctrl + Numpad 3 para a visualização esquerda, adicione sua dobradiça e volte com o teclado numérico 3.

![Etapa 14: Dobradiça PlateL e Dobradiça PlateR](../images/crescent-rose/en/14-plate-hinges.png){.manual-image-155}

*1: Faça dobradiças PlateR e PlateL; use a vista lateral oposta para alcançar PlateL. 2: Defina cada máximo para 30.*

### Passo 15 — Adicionar link → Seguir

Uma alça deve mover ambas as placas. Antes de iniciar o guia, pressione Numpad 1 para vista frontal, selecione `Blade2` e use F3 > Quadro selecionado para aproximar a cabeça. As duas placas externas aparecem nas bordas esquerda e direita. Abra **Add Link > Follow**, clique em `PlateL` na borda esquerda (a parte principal), depois em `PlateR` na borda direita (a parte seguinte) e pressione Enter.

![Etapa 15: a vista frontal expõe ambas as placas externas para as palhetas Seguir](../images/crescent-rose/en/15-follow.png){.manual-image-155}

*1: Clique primeiro em PlateL, a parte principal. 2: Clique em PlateR em segundo lugar, a seguinte parte. Pressione Enter.*

### Passo 16 – Intervalos

Com o novo Seguir selecionado, verifique os **Source Range** 0…30 e**Target Range** 0…30 preenchidos automaticamente. Renomeie-o de `PlateR Follow` para**Name**.

![Etapa 16: Intervalo de origem e intervalo de destino](../images/crescent-rose/en/16-follow-ranges.png){.manual-image-155}

*1: Nomeie o link PlateR Follow. 2: Verifique se o intervalo de origem é de 0 a 30. 3: Verifique se o intervalo de destino é de 0 a 30.*

### Passo 17 — Adicionar Link → Pistão

O suporte deve continuar apontando entre o receptor e a cabeça enquanto a cabeça dobra. Antes de iniciar o guia, pressione Numpad 3 para visualização direita, selecione `StrutRod` no Outliner e use F3 > Frame Selected. Abra **Add Link > Piston**. Defina esta visualização aproximada primeiro; os atalhos de navegação são consumidos enquanto o guia está ativo.

![Etapa 17: menu Adicionar Link, Pistão](../images/crescent-rose/en/17-piston.png){.manual-image-155}

*1: Abra Adicionar link após enquadrar o StrutRod. 2: Escolha Pistão; o guia pede o cilindro primeiro.*

### Passo 18 — O cilindro e a haste

Clique primeiro na parte do cilindro: `StrutBase`, a haste fina, que aparece nos entalhes da luva. Em seguida, clique na parte da haste: `StrutRod`, a manga. Use a visualização aproximada para clicar primeiro na haste vermelha exposta e depois na manga preta. As funções do cilindro/haste da guia descrevem as extremidades do link; os nomes dos objetos deste modelo descrevem suas peças de origem. Pressione Enter para aceitar, renomeie o link `Head Strut` e deixe **Stretch** desativado.

**O que você deveria estar vendo:** Alteração `HeadMount Hinge` nos Controles: o suporte segue, cada parte voltada para a outra. Restaure o valor para zero.

![Etapa 18: a guia do pistão, o cilindro vermelho exposto e depois a luva preta](../images/crescent-rose/en/18-piston-parts.png){.manual-image-100}

*1: Clique primeiro no StrutBase vermelho exposto. 2: Clique na manga preta do StrutRod em segundo lugar. Pressione Enter.*

![Etapa 18: Configurações do Head Strut com Stretch off](../images/crescent-rose/en/18-piston-settings.png){.manual-image-70}

*1: Renomeie o link Head Strut. 2: Deixe Stretch desmarcado; em seguida, teste o HeadMount Hinge e restaure 0.*

## F. O rifle

### Passo 19 — Punho e dobradiças traseiras

**Add Joint → Hinge** em `Grip`, X, Enter,**Min** 0,**Max** 90. Repita em `RearSpike`, X, Enter,**Min** 0,**Max** 90. Em seguida, selecione `RearSpike Hinge` na lista e altere seu `Axis X to -1`, deixando Y e Z em 0. Isso inverte sua direção de dobra para que a ponta traseira volte em direção à cabeça dobrada no Compact; mantenha o Grip no X positivo. Confirme se `Grip Hinge` e `RearSpike Hinge` aparecem na lista de juntas. Esses dois controles dobram a empunhadura e a ponta traseira para obter a forma compacta na Etapa 25.

![Etapa 19: Dobradiça de aperto, máx. 90](../images/crescent-rose/en/19-grip-hinge.png){.manual-image-110}

*1: Selecione Dobradiça de punho. 2: Mantenha o Eixo X em 1, Y e Z em 0. 3: Defina Máx. como 90; mantenha o mínimo em 0.*

![Etapa 19: Dobradiça RearSpike com Eixo X -1 e Max 90](../images/crescent-rose/en/19-rear-hinge.png){.manual-image-155}

*1: Selecione Dobradiça Traseira. 2: Defina o Eixo X como -1. 3: Defina Máx. para 90; mantenha o mínimo em 0.*

### Passo 20 — Slides de revista e parafuso

**Add Joint → Slide** em `Magazine`, pressione Z, Enter,**Max** 0.04. Em seguida, um slide em `Bolt`, Z, Enter,**Max** 0.06. Os slides medem em unidades de cena: 0,06 é 6 cm.

![Etapa 20: Slide da revista, eixo Z e máximo 0,04](../images/crescent-rose/en/20-slides.png){.manual-image-155}

*1: Selecione Slide de revista após Adicionar junta > Slide. 2: Use o eixo Z (Z = 1, X = Y = 0). 3: Defina Máx. como 0,04; mantenha o mínimo em 0.*

![Etapa 20: Bolt Slide, eixo Z e Max 0,06](../images/crescent-rose/en/20-bolt-slide.png){.manual-image-155}

*1: Selecione Deslizar parafuso após Adicionar junta > Deslizar. 2: Use o eixo Z (Z = 1, X = Y = 0). 3: Defina Máx. como 0,06; mantenha o mínimo em 0.*

### Passo 21 — Deslizamento do Pólo

Um slide em `Pole`, Z, Enter, **Max** 0.6. Valores positivos movem o pólo para dentro do receptor. Defina `Pole Slide` como 0,6 pol.**4. Controls** para ver o eixo retrair e, em seguida, restaure-o para zero.

![Etapa 21: Configurações do Pole Slide, eixo Z e Max 0,6](../images/crescent-rose/en/21-pole-slide.png){.manual-image-155}

*1: Selecione Deslizar Pólo após Adicionar Junta > Deslizar. 2: Use o eixo Z (Z = 1, X = Y = 0). 3: Defina Máx. para 0,6; mantenha o mínimo em 0.*

### Passo 22 — Telescópio Pólo

**Add Joint → Telescope**. Clique em `Pole` (a base), depois em `ButtSpike` (o segmento), pressione Enter, pressione Z, pressione Enter. Defina**Length** 0.2. Seu controle separado move a ponta até 20 cm ao longo de Z positivo, para dentro do poste neste modelo. Teste e restaure zero.

![Etapa 22: escolhas guiadas do telescópio, pólo como base e ButtSpike como segmento](../images/crescent-rose/en/22-telescope-pick.png){.manual-image-155}

*1: Clique em Pólo como base. 2: Clique em ButtSpike como segmento. Pressione Enter, depois Z e depois Enter.*

![Etapa 22: configurações do telescópio pólo, eixo Z e comprimento 0,2](../images/crescent-rose/en/22-telescope.png){.manual-image-155}

*1: Selecione Telescópio Pólo. 2: Verifique se Z é o seu eixo. 3: Insira Comprimento 0,2; teste o controle e restaure zero.*

## G. Sequências

### Passo 23 — Adicionar Sequência

Em **3. Sequences**, clique em**Add Sequence** e clique duas vezes em seu nome na lista para renomeá-lo como `Scythe to Rifle`. Pressione Enter.

![Etapa 23: adicionar sequência](../images/crescent-rose/en/23-add-sequence.png){.manual-image-155}

*1: Clique em Adicionar sequência. 2: Clique duas vezes no novo nome e digite Scythe to Rifle. Pressione Enter.*

### Passo 24 — Grave um grupo de movimento

Clique em **Move Slider to End**: o controle deslizante da sequência salta para `100%` e o botão se torna Gravar Etapa 1. Agora coloque o primeiro grupo de movimento com os controles deslizantes em**4. Controls**: `BladeTip Hinge` 70 e `Blade2 Hinge` 120. Clique em Gravar Etapa 1. Isso armazena dois alvos entradas, uma para cada alça movida, e redefine esses dois controles deslizantes conjuntos para zero.

![Etapa 24: mova o controle deslizante para o final antes de posicionar o primeiro grupo](../images/crescent-rose/en/24-capture-step.png){.manual-image-155}

*1: Clique em Mover controle deslizante para terminar uma vez. O botão muda para Gravar Etapa 1.*

![Etapa 24: Grave a Etapa 1 com Blade2 a 120 e BladeTip a 70 graus](../images/crescent-rose/en/24-record-step.png){.manual-image-155}

*1: Digite Blade2 = 120 e BladeTip = 70. 2: Clique em Gravar Etapa 1; ambos os alvos são armazenados e os controles deslizantes conjuntos são redefinidos.*

*Grupos de movimento restantes.* A gravação permanece armada após cada captura. Posicione o próximo grupo e clique no botão Record Step exibido; não arme novamente:

|Grupo de movimento|Coloque essas alças|Botão Gravar após os grupos anteriores|
|---|---|---|
|2|`Blade1 Hinge` 10 e `PlateL Hinge` 30|Gravar Etapa 3|
|3|`HeadMount Hinge` 90|Gravar Etapa 5|
|4|`Pole Slide` 0.6|Gravar Etapa 6|

O número do botão é o número de entradas de destino armazenadas mais um. Gravar duas alças avança dois; não conta cliques de gravação. Os quatro grupos de movimento acima produzem, portanto, seis entradas alvo. Se você alterar quais alças se movem, use o número realmente exibido.

### Passo 25 — Os passos

Cada alvo gravado tem sua própria entrada na sequência, mostrando seu **Target**, sua facilidade e seu**Start** e**End** no controle deslizante. Dê a ambas as entradas em cada grupo de movimento o mesmo Início e Fim: a lâmina dobra primeiro (0…0,25), as placas e o primeiro segmento em seguida (0,25…0,5), a cabeça em terceiro (0,5…0,8) e o mastro por último (0,8…1). Antes da sua fatia, um passo permanece no seu valor inicial; após sua fatia, ele mantém seu valor final. Os campos Início/Fim usam 0-1, enquanto os controles deslizantes mostram 0-100%.

Mantenha cada entrada em `Ease In Out`. Em seguida, adicione uma segunda sequência, `Rifle to Compact`: primeiro registro `Grip Hinge` 90 e `RearSpike Hinge` 90 (duas entradas, ambas 0…0,5); em seguida, registre `Magazine Slide` 0,04 e `Bolt Slide` 0,06 (duas entradas, ambas 0,5…1). Seu botão de gravação muda de Record Step 1 para Record Step 3 para o segundo grupo. Após a conclusão de cada sequência, clique em **Cancel** no banner de captura. Isso encerra a gravação, retém as entradas armazenadas e retorna o controle deslizante de sequência para zero. Um aviso de sobreposição enquanto armado descreve o próximo intervalo de gravação proposto; não adicione um grupo vazio extra.

![Etapa 25: todos os seis alvos e intervalos de tempo em Scythe to Rifle](../images/crescent-rose/en/25-sequence-steps.png){.manual-image-155}

*1: Meta é o valor conjunto registrado. 2: Escolha Facilidade de entrada. 3: Entre em Iniciar. 4: Digite Fim. Repita esses campos para todas as seis entradas usando os valores mostrados.*

![Etapa 25: todos os quatro alvos e intervalos de tempo em Rifle to Compact](../images/crescent-rose/en/25-compact-steps.png){.manual-image-155}

*1: Grip e RearSpike usam Target 90, Start 0, End 0.5. 2: O carregador e o parafuso usam 0,04 / 0,06, início 0,5, fim 1. Mantenha a facilidade dentro e fora.*

![Passo 25: finalize a gravação com Cancelar no banner de captura](../images/crescent-rose/en/25-cancel-capture.png){.manual-image-135}

*1: Após finalizar uma sequência, clique em Cancelar neste banner de captura para finalizar a gravação. Isso mantém as entradas e retorna a sequência para zero.*

### Passo 26 — Teste a sequência

Clique em **Test** próximo ao botão de gravação passo a passo. O controle deslizante varia de 0% a 100% a 0% e, em seguida, restaura seu valor anterior ao teste. Teste `Scythe to Rifle` da Scythe; teste `Rifle to Compact` com a primeira sequência em 100%. Retorne ambos para 0% depois.

![Passo 26: o botão Teste de sequência durante a dobra](../images/crescent-rose/en/26-sequence-test.png){.manual-image-155}

*1: Clique em Testar ao lado do botão de gravação. 2: Observe a dobra e retorne. Teste compacto com foice para rifle em 100%.*

**O que você deveria ver:** A lâmina se curva, as placas se fecham, a cabeça se dobra ao longo do receptor e o mastro desliza para cima. Depois tudo volta.

## H. Formulários

### Passo 27 — Salvar Formulário

Em **4. Controls**, com cada controle deslizante em 0, clique em**Save Form** e clique duas vezes na nova entrada da lista para nomeá-la como `Scythe`. Defina `Scythe to Rifle` como `100%` e salve/nomeie `Rifle`. Defina `Rifle to Compact` como `100%` também e salve/nomeie `Compact`. Deixe todos os controles deslizantes de juntas individuais em zero: as sequências fornecem seu movimento. Definir a sequência selecionada até o fim pode armar a gravação novamente; salvar um formulário não registra outra etapa. Escolher `Scythe` e**Go to Form** retorna ambas as sequências para zero e limpa o estado armado. Ir para Rifle ou Compact pode armar a gravação novamente porque a sequência selecionada está em 100%; não clique em Etapa de registro, a menos que pretenda adicionar outro destino.

![Etapa 27: salve o formulário com todos os controles deslizantes em 0](../images/crescent-rose/en/27-save-form.png){.manual-image-155}

*1: Comece com ambas as sequências e todas as juntas em 0. 2: Clique em Salvar Formulário. 3: Clique duas vezes na nova entrada da lista e nomeie-a como Scythe; repita para Rifle e Compacto.*

### Passo 28 — Vá para o Formulário

Clique em um formulário na lista e clique em **Go to Form**.**Go and Key** faz o mesmo e codifica todos os controles no quadro atual, que é como você anima a transformação.

![Etapa 28: Rifle selecionado, vá para o formulário](../images/crescent-rose/en/28-go-to-form.png){.manual-image-155}

*1: Selecione o formulário salvo. 2: Clique em Ir para o formulário. Go and Key também insere chaves de animação.*

### Passo 29 — O rifle

![Etapa 29: o formulário Rifle](../images/crescent-rose/en/29-result-rifle.png){.manual-image-155}

*1: Selecione Rifle. 2: Clique em Ir para o formulário. 3: Verifique as porcentagens da sequência em relação à pose retratada.*

### Passo 30 – Compacto

![Etapa 30: o formulário compacto](../images/crescent-rose/en/30-result-compact.png){.manual-image-155}

*1: Selecione Compacto. 2: Clique em Ir para o formulário. 3: Verifique as porcentagens da sequência em relação à pose retratada.*

Volte para `Scythe` e salve o arquivo.

## O que você construiu

|Gravar|Ossos|O que isso faz|
|---|---|---|
|15 partes|`MCH-<part>` e `DEF-<part>` |A malha de cada parte é parente de seu osso `DEF-` |
|8 dobradiças, 3 corrediças, 1 telescópio|`CTRL-<part>` |As alças; seus valores são os controles deslizantes em **4. Controls** |
|1 pistão|`MCH-<part>-aim` e `MCH-<part>-target` |Mantenha as duas partes do suporte apontadas uma para a outra|
|1 Seguir|nenhum|`PlateR` gira com `PlateL` |
|2 sequências|`CTRL-SEQ-<name>` |Um controle deslizante cada|
|3 formulários|nenhum|Valores do controle deslizante salvos|

O exemplo atualizado foi aprovado no Rig Validator sem problemas relatados. Ele também passou nas verificações de recarga com a execução automática de scripts Python desativada, incluindo todos os controles individuais e todos os três formulários.

## Tente a seguir

- Marque **Curve** em `PlateR Follow` e remodele o mapeamento no Editor de Gráfico.
- Salve uma quarta forma, `Carry`, com a lâmina dobrada, mas com a cabeça levantada.
- Codifique os formulários sobre os quadros com **Go and Key** e, em seguida, exporte os ossos `DEF-` (consulte [Ferramentas VRChat](08-vrchat.md) ).

## Elo de engrenagem

Crescent Rose não possui par de engrenagens, portanto este rig não possui Gear Link. Um Gear Link gira uma dobradiça quando outra gira, por uma proporção de dentes: uma manivela e uma roda, ou uma cremalheira que transforma a rotação em um slide. Consulte [Elo de engrenagem](07-mechanisms.md#gear-link-ligação-de-engrenagem).

## Créditos

Modelo Crescent Rose de amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; dividido em partes, dimensionadas e manipuladas para este tutorial. Crescent Rose é um projeto da Rooster Teeth Productions; este é um recurso tutorial feito por um fã.

[← Conteúdo](index.md)
