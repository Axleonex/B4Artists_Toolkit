# Tutorial: Crescent Rose com Mechanisms

[← Sumário](index.md)

<style>
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

Crescent Rose é uma foice que também vira rifle. Você vai rigar seu modelo com Mechanisms: um slider transforma a foice em rifle e outro dobra o rifle na forma compacta. Usará todos os tipos atuais de junta e ligação exceto Gear Link: oito Hinges, três Slides, um Telescope, um Piston, um Follow, duas Sequences e três Forms.

As formas são poses didáticas deste modelo de fã. Mechanisms não detecta colisões nem cria uma réplica mecanicamente projetada: inspecione as folgas ao adaptar o rig.

Resultado: `examples/crescent-rose/CrescentRose_Mechanisms.blend`. Abra a qualquer momento para comparar.

## Antes de começar

- Arquivos: comece em `examples/crescent-rose/CrescentRose_parts.blend`, modelo dividido em 15 objetos. `CrescentRose_Mechanisms.blend` contém o rig final.
- Tempo: reserve uma sessão para preparar o FBX e outra para Mechanisms. São exercícios extensos; salve entre etapas.
- Vocabulário: leia primeiro a introdução de [Mechanisms](07-mechanisms.md): define peça, junta, ligação, controle, Sequence e Form.
- Idioma: capturas mostram Bforartists e BoneCraft em inglês. Os painéis BoneCraft seguem **Language** nas suas preferências; o restante segue o idioma de Bforartists. Num idioma não traduzido por BoneCraft, seus painéis permanecem em inglês e esta edição continua válida.
- Início: use P1-P8 para o FBX original ou pule ao passo 1 com o arquivo preparado. Ambos usam as mesmas 15 peças.
- Versão: instruções e capturas reais verificadas com BoneCraft `9.1.2` em Bforartists `5.2.0`, mapa de teclas padrão.

Números vermelhos indicam onde clicar, digitar ou inspecionar. Siga a ordem da legenda (1, 2, 3); a numeração reinicia a cada imagem. Resultado em caixa é uma verificação; peça ou botão circulado é alvo de interação.

## Preparar o FBX original (P1-P8)

Ignore com `CrescentRose_parts.blend`. Trabalhe num arquivo novo; mantenha FBX e pasta `CrescentRoseTextures` juntos. Passos repetidos em Bforartists 5.2.0 com atalhos padrão. Use o menu de modos: Tab pode alternar sobreposições em vez de entrar em Edit Mode.

### P1 - Importar o FBX

Cena vazia: **File > Import > FBX (.fbx) (Legacy)**, selecione `CrescentRose.fbx`, Scale `1.00`. Use o importador Legacy. O Outliner mostra uma raiz e três malhas de materiais: `Black01`, `Blades01`, `Red01`. Numpad 3 dá a vista direita; Home enquadra.

![P1 - Importar o FBX](../images/crescent-rose/en/prep-01-import-fbx.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Selecione CrescentRose.fbx. 2: Scale 1.00. 3: Import FBX com o importador Legacy.*

### P2 - Preservar posição e definir tamanho

Em Object Mode selecione as três malhas. Use **Object > Parent > Clear and Keep Transformation** e remova a raiz agora sem uso. Com as três selecionadas, **Object > Apply > Rotation & Scale**. A arma importada mede aproximadamente `0.32 m`. Escale as três juntas por `6.25` (Ctrl+R inicia Scale neste mapa Bforartists; digite 6.25 e confirme), depois aplique Rotation & Scale novamente. A altura total fica aproximadamente `1.997 m`. Faça uma vez; o arquivo preparado já está escalado.

![P2 - Preservar posição e definir tamanho](../images/crescent-rose/en/prep-02-unparent-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: F3, busque Clear Parent Keep Transform. 2: Clear and Keep Transformation nas três malhas antes de remover a raiz.*

![P2 - Preservar posição e definir tamanho](../images/crescent-rose/en/prep-02-scale.png){style="max-width:100%;max-height:115mm;width:auto;height:auto"}

*1: Após escalar juntas por 6.25, aplique Rotation & Scale; Rotation deve ser 0. 2: Scale 1 em todos os eixos.*

Dimensions de um objeto mede apenas aquela malha de material. Meça a extensão total de baixo a cima da arma. Os três objetos precisam ter rotação zero e escala 1 antes de separar.

### P3 - Conectar os materiais

Use a área Shading e Material Preview. Para cada material, carregue suas imagens `BaseColor`, `Metallic`, `Roughness`, `Normal` de `CrescentRoseTextures`. Ligue Image Texture Color à entrada correspondente de Principled BSDF. BaseColor usa **sRGB**; os outros usam `Non-Color`. Para Normal, insira **Normal Map**, mantenha `Tangent Space`, ligue Color da imagem a Color do nó e sua saída Normal a BSDF Normal. Preserve os UVs.

![P3 - Conectar os materiais](../images/crescent-rose/en/prep-03-materials.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: BaseColor Color para BSDF Base Color. 2: BaseColor em sRGB. 3: Mapas de dados em Non-Color. 4: Imagem Normal > Normal Map > BSDF Normal, Tangent Space.*

![P3 - Conectar os materiais](../images/crescent-rose/en/prep-03-shaded.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Confira o material da lâmina. 2: Confira vermelho/preto em Material Preview; nenhuma textura ausente rosa.*

Repita para os materiais vermelho e da lâmina. Confira o espaço de cor após escolher cada imagem; a configuração pertence à imagem. A arma deve ser vermelha, preta e metálica, sem rosa de textura ausente.

### P4 - Separar partes soltas

Selecione as três malhas, escolha **Edit Mode** no menu, selecione toda a geometria e use **Mesh > Separate > By Loose Parts**. Volte ao Object Mode: há **37** objetos de malha. Sufixos numéricos podem variar; identifique por forma e posição.

![P4 - Separar partes soltas](../images/crescent-rose/en/prep-04-separate-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Edit Mode, selecione toda a geometria. 2: F3, busque Separate Loose, escolha By Loose Parts.*

![P4 - Separar partes soltas](../images/crescent-rose/en/prep-04-separate.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Confira 37 objetos. 2: Selecione pelo Outliner por forma e posição; sufixos podem variar.*

### P5 - Unir os 15 grupos móveis

Selecione peças que se movem juntas e use **Object > Join** (Ctrl+J); renomeie no Outliner. Nas peças opostas, orbite para selecionar ambos os lados e confira antes de unir. Trabalhe da ponta da lâmina para dentro, depois corpo e haste. A tabela inclui cada ilha original; o material descreve aparência, não o nome final.

| Objeto final | Peças a unir | Vértices |
|---|---|---:|
| `BladeTip` | Botão preto da junta da ponta e espigão metálico | 252 |
| `Blade2` | Duas placas metálicas do segundo segmento e duas coberturas vermelhas | 1000 |
| `Blade1` | Duas placas metálicas do primeiro segmento junto à cabeça | 512 |
| `HeadMount` | Bloco traseiro preto, tampa superior e núcleo; duas placas vermelhas internas e duas tampas finas superiores | 1395 |
| `PlateL` | Placa vermelha externa no X negativo | 676 |
| `PlateR` | Placa vermelha externa no X positivo | 676 |
| `RearSpike` | Duas lâminas metálicas, duas tampas vermelhas do pivô e duas placas vermelhas de suporte | 1194 |
| `Receiver` | Corpo preto e botão pequeno, anel metálico acima do ferrolho, carcaça vermelha longa | 2609 |
| `Grip` | Bloco vermelho do punho sob o corpo | 194 |
| `Magazine` | Tubo preto sob o corpo | 96 |
| `Bolt` | Cilindro vermelho do ferrolho e suas duas peças de botão | 362 |
| `Pole` | Haste inferior metálica e colar vermelho | 148 |
| `ButtSpike` | Espigão metálico inferior | 110 |
| `StrutBase` | Vareta vermelha fina entre corpo e cabeça | 34 |
| `StrutRod` | Manga preta entalhada em volta da vareta | 108 |

Total: **15 malhas e 9.366 vértices**. Não una placas externas a Blade1, nem as duas peças da escora entre si. A escora já vem separada; dispensa bisect. O passo 2 repete os nomes finais e parentes futuros.

![P5 - Unir os 15 grupos móveis](../images/crescent-rose/en/prep-05-group-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Renomeie os 15 grupos no Outliner conforme a tabela.*

![P5 - Unir os 15 grupos móveis](../images/crescent-rose/en/prep-05-blade1.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Selecione as duas placas metálicas Blade1 opostas. 2: Confira ambas, use Join e renomeie Blade1.*

![P5 - Unir os 15 grupos móveis](../images/crescent-rose/en/prep-05-join-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Abra Object após selecionar apenas um grupo. 2: Join (Ctrl+J). O recorte mostra o comando; use a seleção de duas peças acima.*

### P6 - Centralizar as origens

Em Object Mode selecione as 15 malhas. **Object > Set Origin > Origin to Geometry**, opção Center: `Bounds Center`. Confira rotação zero e escala 1. Ainda não há pais nem armadura. São origens de preparação; no passo 6 os pivôs vão às juntas reais.

![P6 - Centralizar as origens](../images/crescent-rose/en/prep-06-origin-command.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Object. 2: Passe sobre Set Origin. 3: Origin to Geometry; Bounds Center nas opções.*

![P6 - Centralizar as origens](../images/crescent-rose/en/prep-06-origins.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Origem laranja centrada na malha. 2: Rotation 0. 3: Scale 1. Pivôs do mecanismo serão movidos depois.*

### P7 - Redimensionar e empacotar texturas

No Image Editor escolha cada um dos **12 mapas usados** (quatro por material). **Image > Resize**, largura e altura **1024**, confirme e use **Image > Pack**. Repita em todos os mapas. Pack guarda os pixels redimensionados no blend; não sobrescreva os JPEGs originais. Confira Material Preview.

![P7 - Redimensionar e empacotar texturas](../images/crescent-rose/en/prep-07-pack-textures.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Image > Resize, largura e altura 1024. 2: Confira 1024 × 1024. 3: Pack. Repita nos 12 mapas.*

### P8 - Salvar e reabrir o arquivo preparado

Salve a cópia como `CrescentRose_parts.blend`. Reabra, confira 15 malhas nomeadas, transformações e materiais vermelho/preto. Os 12 mapas devem funcionar sem o diretório original. Use vista direita e Home; continue no passo 1.

![P8 - Salvar e reabrir o arquivo preparado](../images/crescent-rose/en/prep-08-save-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: File para Save As, depois Open para recarregar. 2: Confira as 15 malhas nomeadas. 3: Confira materiais; o título identifica o arquivo reaberto.*

## A. Abrir o arquivo



### Passo 1 — Abrir o arquivo das peças

Abra `examples/crescent-rose/CrescentRose_parts.blend`. Use Material Preview e Numpad 3 para a vista direita: lâmina aponta à esquerda, espigão inferior para baixo. Home enquadra a arma.

![Passo 1 — Abrir o arquivo das peças](../images/crescent-rose/en/01-open-file.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Material Preview. 2: Numpad 3 até Right Orthographic; Home enquadra.*

**Resultado esperado:** foice vermelha e preta, cerca de 2 m, nada selecionado.

### Passo 2 — Conhecer as peças

O Outliner contém 15 objetos, cada um movendo-se como bloco:

| Objeto | Descrição | Rides on |
|---|---|---|
| `Receiver` | Corpo do rifle com luneta, gatilho e mira | o rig |
| `Grip` | Punho sob o corpo | `Receiver` |
| `Magazine` | Carregador cilíndrico | `Receiver` |
| `Bolt` | Ferrolho | `Receiver` |
| `Pole` | Haste inferior e colar | `Receiver` |
| `ButtSpike` | Espigão inferior | `Pole` |
| `HeadMount` | Bloco de suporte da lâmina | `Receiver` |
| `Blade1` | Primeiro segmento junto à cabeça | `HeadMount` |
| `Blade2` | Segundo segmento | `Blade1` |
| `BladeTip` | Ponta | `Blade2` |
| `RearSpike` | Espigão atrás da cabeça | `HeadMount` |
| `PlateL`, `PlateR` | Placas laterais externas da cabeça | `HeadMount` |
| `StrutBase` | Vareta fina entre corpo e cabeça | `Receiver` |
| `StrutRod` | Manga entalhada da vareta | `HeadMount` |

![Passo 2 — Conhecer as peças](../images/crescent-rose/en/02-the-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Identifique os três segmentos. 2: Compare nomes de corpo, cabeça e haste com a tabela. 3: Mantenha StrutBase e StrutRod separados.*

Para o FBX original, siga P1-P8. O arquivo preparado fornecido resulta dessas ações de interface; o script do repositório contém uma tabela de agrupamento de referência.

### Passo 3 — Encontrar Mechanisms

Abra BoneCraft na Tool Shelf esquerda (se oculta, T sobre a viewport e Tools em Region Toggle) e expanda **Mechanisms**. Arraste a borda direita para dar espaço ao texto. A mesma seção existe em **Properties > Scene** quando Scene Properties está em Show nas preferências BoneCraft. As capturas usam a Tool Shelf. Com malha ativa e sem rig, localize **Add Parts from Selection** no topo. Selecione todas as peças no passo 4 antes de clicar; as subseções numeradas ficam utilizáveis após o acréscimo.

![Passo 3 — Encontrar Mechanisms](../images/crescent-rose/en/03-mechanisms-section.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Aba BoneCraft. 2: Mechanisms. 3: Localize Add Parts from Selection; selecione as malhas antes de usar.*

## B. Peças



### Passo 4 — Add Parts from Selection

Ponteiro na viewport, A seleciona os 15 objetos. Clique em **Add Parts from Selection**.

![Passo 4 — Add Parts from Selection](../images/crescent-rose/en/04-add-parts.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: A na viewport seleciona as 15 malhas. 2: Add Parts from Selection.*

**Resultado esperado:** nova armadura “Mechanism Rig” no Outliner, com as peças abaixo. As malhas continuam selecionadas. **1. Parts** lista as 15 peças; BoneCraft agora começa com Overview do rig, que pode recolher.

### Passo 5 — Rides on

A peça acompanha aquela à qual está presa. Selecione `Blade1` em **1. Parts**, abra “Rides on” abaixo da lista e escolha `HeadMount`. Repita conforme a tabela do passo 2. `Receiver` mantém “the rig”.

![Passo 5 — Rides on](../images/crescent-rose/en/05-rides-on.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade1 na lista Parts. 2: Rides on → HeadMount. Repita com a tabela de pais.*

### Passo 6 — Pivôs

Uma dobradiça gira no pivô da peça. Lâminas, cabeça e punho devem girar nas juntas, não no centro. Com `Blade1` na lista, **Edit Pivot**, selecione o marcador, Ctrl+W para Move no Bforartists, posicione na junção lâmina/cabeça e **Apply Pivot**. Use vista ortográfica lateral para preservar a posição transversal. Repita em `Blade2` (junção Blade1), `BladeTip` (junção Blade2), `HeadMount` (ponto inferior onde chega a escora), `Grip` (borda superior), `RearSpike` (junção cabeça), `PlateL` e `PlateR` (centro do parafuso redondo na junção Blade1/cabeça), `StrutBase` (base), `StrutRod` (topo). A captura orienta; poucos milímetros não mudam visivelmente o resultado.

![Passo 6 — Pivôs](../images/crescent-rose/en/06-edit-pivot-button.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Blade1 em Parts. 2: Edit Pivot; mova e aplique o marcador como abaixo.*

![Passo 6 — Pivôs](../images/crescent-rose/en/06-edit-pivot.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Ctrl+W leva o marcador à junta da lâmina. 2: Apply Pivot preserva o local.*

## C. Cabeça



### Passo 7 — Add Joint → Hinge

Abra **Add Joint → Hinge**. O guia começa; cabeçalho e barra de status explicam cada etapa.

![Passo 7 — Add Joint → Hinge](../images/crescent-rose/en/07-head-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Joint. 2: Hinge. O guia agora espera uma peça.*

### Passo 8 — Clicar na cabeça

O cabeçalho pede a peça que gira. Na vista direita a placa externa cobre a cabeça: clique no bloco traseiro atrás das placas (círculo). Se indicar `PlateR`, Esc, reinicie **Add Joint > Hinge** e clique mais atrás. Oculte obstáculos antes de iniciar: o guia intercepta os atalhos comuns.

![Passo 8 — Clicar na cabeça](../images/crescent-rose/en/08-head-hinge-click.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Bloco preto traseiro de HeadMount, atrás da placa vermelha. Confira o nome HeadMount.*

### Passo 9 — X e Enter

O cabeçalho pede o eixo. Pressione X: a cabeça gira no eixo transversal, com prévia em ciclo. Enter confirma.

![Passo 9 — X e Enter](../images/crescent-rose/en/09-head-hinge-axis.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: No pedido do eixo, X e Enter. 2: Observe a rotação no pivô antes de confirmar.*

**Resultado esperado:** `HeadMount Hinge` em **2. Joints & Links**, seu slider em **4. Controls**. Use sliders em Object Mode. Para controles de ossos na viewport, selecione a armadura e entre em Pose Mode.

### Passo 10 — Limites

Selecione `HeadMount Hinge` na lista: **Min** 0, **Max** 120. Valores positivos giram a cabeça para baixo e para trás. Preserve o limite de 120 graus; Rifle usará alvo de 90 graus com as dobradiças da lâmina.

![Passo 10 — Limites](../images/crescent-rose/en/10-head-hinge-limits.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: HeadMount Hinge. 2: Min 0. 3: Max 120; clique duplo no número, digite e Enter.*

### Passo 11 — Testar

Clique no botão de reprodução da linha. A cabeça vai a 120°, volta e a pose é restaurada.

![Passo 11 — Testar](../images/crescent-rose/en/11-test-head.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Triângulo de reprodução de HeadMount Hinge. Observe ida e volta.*

## D. Cadeia da lâmina



### Passo 12 — Mais três dobradiças

Repita 7 a 10 em `Blade1`, `Blade2`, `BladeTip`: **Add Joint → Hinge**, clique no segmento, X, Enter, **Max** 120. Cada segmento acompanha o anterior: as três dobradiças formam uma cadeia.

![Passo 12 — Mais três dobradiças](../images/crescent-rose/en/12-blade-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Crie e selecione as dobradiças Blade1, Blade2, BladeTip. 2: Max 120 e eixo X em cada uma.*

### Passo 13 — Testar a cadeia

Recolha **2. Joints & Links**, expanda **4. Controls**. Em Object Mode, defina `Blade1 Hinge`, `Blade2 Hinge` e `BladeTip Hinge` em 60 graus, um de cada vez. Clique duplo no campo, Ctrl+A, valor, Enter. Segmentos posteriores acompanham anteriores e a cadeia enrola. Volte os três a 0.

![Passo 13 — Testar a cadeia](../images/crescent-rose/en/13-blade-chain.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: 60 nos três sliders da lâmina. 2: Confira o enrolamento conjunto. Restaure os três a 0.*

## E. Placas e escora



### Passo 14 — Dobradiças das placas

Adicione Hinge em `PlateR`, **Max** 30. `PlateL` fica atrás da cabeça na vista direita: Ctrl+Numpad 3 para vista esquerda, adicione sua Hinge e volte com Numpad 3.

![Passo 14 — Dobradiças das placas](../images/crescent-rose/en/14-plate-hinges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Crie as dobradiças PlateR e PlateL; mude de lado para atingir PlateL. 2: Max 30 em cada uma.*

### Passo 15 — Add Link → Follow

Um controle deve mover ambas as placas. Antes do guia: Numpad 1 para frente, selecione `Blade2`, F3 > Frame Selected para aproximar a cabeça. Placas nas extremidades esquerda/direita. **Add Link > Follow**, clique `PlateL` à esquerda (líder), depois `PlateR` à direita (seguidora), Enter.

![Passo 15 — Add Link → Follow](../images/crescent-rose/en/15-follow.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: PlateL primeiro, líder. 2: PlateR depois, seguidora. Enter.*

### Passo 16 — Intervalos

Com Follow selecionado, confira **Source Range** 0…30 e **Target Range** 0…30 preenchidos automaticamente. Em **Name**, renomeie `PlateR Follow`.

![Passo 16 — Intervalos](../images/crescent-rose/en/16-follow-ranges.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Nome PlateR Follow. 2: Source Range 0 a 30. 3: Target Range 0 a 30.*

### Passo 17 — Add Link → Piston

A escora precisa apontar entre corpo e cabeça enquanto esta dobra. Antes do guia: Numpad 3, selecione `StrutRod` no Outliner, F3 > Frame Selected. **Add Link > Piston**. Aproxime antes: o guia intercepta atalhos de navegação.

![Passo 17 — Add Link → Piston](../images/crescent-rose/en/17-piston.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Link após enquadrar StrutRod. 2: Piston; o guia pede o cilindro primeiro.*

### Passo 18 — Cilindro e haste

Clique primeiro no cilindro: `StrutBase`, vareta fina visível nos entalhes da manga. Depois na haste: `StrutRod`, a manga. Na vista próxima, clique no vermelho exposto antes do preto. Os papéis cilindro/haste descrevem as pontas da ligação; os nomes descrevem peças do modelo original. Enter, nome `Head Strut`, **Stretch** desligado.

**Resultado esperado:** altere `HeadMount Hinge` em Controls: as duas peças da escora apontam uma à outra. Restaure zero.

![Passo 18 — Cilindro e haste](../images/crescent-rose/en/18-piston-parts.png){style="max-width:100%;max-height:100mm;width:auto;height:auto"}

*1: StrutBase vermelho exposto primeiro. 2: Manga preta StrutRod depois. Enter.*

![Passo 18 — Cilindro e haste](../images/crescent-rose/en/18-piston-settings.png){style="max-width:100%;max-height:70mm;width:auto;height:auto"}

*1: Nome Head Strut. 2: Stretch desmarcado; teste HeadMount Hinge e restaure 0.*

## F. Rifle



### Passo 19 — Dobradiças do punho e espigão traseiro

**Add Joint → Hinge** em `Grip`, X, Enter, **Min** 0, **Max** 90. Repita em `RearSpike`, X, Enter, **Min** 0, **Max** 90. Selecione `RearSpike Hinge`, ajuste `Axis X para -1`, Y e Z em 0. Isso inverte a dobra em direção à cabeça recolhida em Compact; Grip mantém X positivo. Confira ambas na lista. Elas dobram punho e espigão traseiro no passo 25.

![Passo 19 — Dobradiças do punho e espigão traseiro](../images/crescent-rose/en/19-grip-hinge.png){style="max-width:100%;max-height:110mm;width:auto;height:auto"}

*1: Grip Hinge. 2: Axis X 1, Y/Z 0. 3: Max 90, Min 0.*

![Passo 19 — Dobradiças do punho e espigão traseiro](../images/crescent-rose/en/19-rear-hinge.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: RearSpike Hinge. 2: Axis X -1. 3: Max 90, Min 0.*

### Passo 20 — Slides de Magazine e Bolt

**Add Joint → Slide** em `Magazine`, Z, Enter, **Max** 0.04. Depois Slide em `Bolt`, Z, Enter, **Max** 0.06. Valores em unidades da cena: 0.06 = 6 cm.

![Passo 20 — Slides de Magazine e Bolt](../images/crescent-rose/en/20-slides.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Magazine Slide após Add Joint > Slide. 2: Eixo Z (Z = 1, X = Y = 0). 3: Max 0.04, Min 0.*

![Passo 20 — Slides de Magazine e Bolt](../images/crescent-rose/en/20-bolt-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Bolt Slide após Add Joint > Slide. 2: Eixo Z (Z = 1, X = Y = 0). 3: Max 0.06, Min 0.*

### Passo 21 — Pole Slide

Slide em `Pole`, Z, Enter, **Max** 0.6. Positivos retraem a haste para cima no corpo. Defina `Pole Slide` em 0.6 em **4. Controls** para conferir, depois restaure zero.

![Passo 21 — Pole Slide](../images/crescent-rose/en/21-pole-slide.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Slide após Add Joint > Slide. 2: Eixo Z (Z = 1, X = Y = 0). 3: Max 0.6, Min 0.*

### Passo 22 — Pole Telescope

**Add Joint → Telescope**. Clique `Pole` (base), `ButtSpike` (segmento), Enter, Z, Enter. **Length** 0.2. Seu controle independente move o espigão até 20 cm em Z positivo, para dentro da haste. Teste e restaure zero.

![Passo 22 — Pole Telescope](../images/crescent-rose/en/22-telescope-pick.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole como base. 2: ButtSpike como segmento. Enter, Z, Enter.*

![Passo 22 — Pole Telescope](../images/crescent-rose/en/22-telescope.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Pole Telescope. 2: Confira eixo Z. 3: Length 0.2; teste e restaure zero.*

## G. Sequências



### Passo 23 — Add Sequence

Em **3. Sequences**, **Add Sequence**, clique duplo no nome da lista e digite `Scythe to Rifle`. Enter.

![Passo 23 — Add Sequence](../images/crescent-rose/en/23-add-sequence.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Add Sequence. 2: Clique duplo no nome, Scythe to Rifle, Enter.*

### Passo 24 — Gravar um grupo de movimentos

**Move Slider to End** leva a sequência a `100%` e vira Record Step 1. Pose o primeiro grupo em **4. Controls**: `BladeTip Hinge` 70, `Blade2 Hinge` 120. Record Step 1 grava dois alvos, um por controle movido, e retorna esses dois sliders a zero.

![Passo 24 — Gravar um grupo de movimentos](../images/crescent-rose/en/24-capture-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Clique uma vez em Move Slider to End. O botão vira Record Step 1.*

![Passo 24 — Gravar um grupo de movimentos](../images/crescent-rose/en/24-record-step.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Blade2 = 120, BladeTip = 70. 2: Record Step 1 guarda ambos e redefine os sliders.*

*Grupos seguintes.* A gravação permanece armada após capturar. Pose o próximo grupo e clique no Record Step exibido, sem armar novamente:

| Grupo | Controles a posar | Botão após grupos anteriores |
|---|---|---|
| 2 | `Blade1 Hinge` 10 e `PlateL Hinge` 30 | Record Step 3 |
| 3 | `HeadMount Hinge` 90 | Record Step 5 |
| 4 | `Pole Slide` 0.6 | Record Step 6 |

O número é a quantidade de alvos guardados mais um. Dois controles avançam por dois; não conta cliques. Os quatro grupos produzem seis alvos. Se alterar os controles, siga o número exibido.

### Passo 25 — As etapas

Cada alvo gravado tem entrada na sequência com **Target**, suavização, **Start** e **End** no slider. Use os mesmos Start/End nas duas entradas de um grupo: lâmina primeiro (0…0.25), placas e primeiro segmento (0.25…0.5), cabeça (0.5…0.8), haste (0.8…1). Antes do intervalo mantém valor inicial; depois mantém o final. Start/End usam 0–1; os sliders de Controls mostram 0–100%.

Mantenha `Ease In Out`. Adicione `Rifle to Compact`: grave `Grip Hinge` 90 e `RearSpike Hinge` 90 (duas entradas 0…0.5); depois `Magazine Slide` 0.04 e `Bolt Slide` 0.06 (duas entradas 0.5…1). O botão passa de Record Step 1 a Record Step 3 no segundo grupo. Ao concluir cada sequência, **Cancel** na faixa de captura encerra a gravação, preserva entradas e retorna o slider a zero. O aviso de sobreposição enquanto armada refere-se ao próximo intervalo proposto; não adicione grupo vazio.

![Passo 25 — As etapas](../images/crescent-rose/en/25-sequence-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Target é o valor de junta gravado. 2: Ease In Out. 3: Start. 4: End. Repita nas seis entradas com os valores mostrados.*

![Passo 25 — As etapas](../images/crescent-rose/en/25-compact-steps.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Grip e RearSpike: Target 90, Start 0, End 0.5. 2: Magazine e Bolt: 0.04 / 0.06, Start 0.5, End 1. Mantenha Ease In Out.*

![Passo 25 — As etapas](../images/crescent-rose/en/25-cancel-capture.png){style="max-width:100%;max-height:135mm;width:auto;height:auto"}

*1: Após terminar a sequência, Cancel nesta faixa encerra captura, preserva entradas e retorna a sequência a zero.*

### Passo 26 — Testar a sequência

Clique **Test** junto ao botão de gravação. O slider vai de 0% a 100% e 0%, depois restaura o valor anterior. Teste `Scythe to Rifle` a partir de Scythe; `Rifle to Compact` com a primeira sequência em 100%. Depois retorne ambas a 0%.

![Passo 26 — Testar a sequência](../images/crescent-rose/en/26-sequence-test.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Test junto à gravação. 2: Observe dobra e retorno. Teste Compact com Scythe to Rifle em 100%.*

**Resultado esperado:** lâmina enrola, placas fecham, cabeça dobra ao longo do corpo, haste retrai. Depois tudo retorna.

## H. Formas



### Passo 27 — Save Form

Em **4. Controls**, todos os sliders a 0, **Save Form**, clique duplo na entrada para nomear `Scythe`. Defina `Scythe to Rifle` em `100%`, salve e nomeie `Rifle`. Ponha também `Rifle to Compact` em `100%`, salve e nomeie `Compact`. Sliders individuais de junta permanecem em zero: sequências fornecem movimento. Levar a sequência selecionada ao fim pode armar gravação; salvar Form não grava outra etapa. `Scythe` e **Go to Form** retornam ambas a zero e desarmam. Rifle ou Compact podem rearmar pois a sequência selecionada chega a 100%; só clique Record Step se quiser acrescentar alvo.

![Passo 27 — Save Form](../images/crescent-rose/en/27-save-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Ambas as sequências e todas as juntas a 0. 2: Save Form. 3: Clique duplo, nome Scythe; repita em Rifle e Compact.*

### Passo 28 — Go to Form

Selecione a forma e clique **Go to Form**. **Go and Key** faz o mesmo e insere chave em cada controle no quadro atual, animando a transformação.

![Passo 28 — Go to Form](../images/crescent-rose/en/28-go-to-form.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Forma salva. 2: Go to Form. Go and Key também insere chaves de animação.*

### Passo 29 — Rifle

![Passo 29 — Rifle](../images/crescent-rose/en/29-result-rifle.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Rifle. 2: Go to Form. 3: Confira percentuais das sequências com a pose ilustrada.*

### Passo 30 — Compact

![Passo 30 — Compact](../images/crescent-rose/en/30-result-compact.png){style="max-width:100%;max-height:155mm;width:auto;height:auto"}

*1: Compact. 2: Go to Form. 3: Confira percentuais das sequências com a pose ilustrada.*

Volte a `Scythe` e salve.

## O que você construiu

| Elemento | Ossos | Função |
|---|---|---|
| 15 peças | `MCH-<part>` e `DEF-<part>` | Cada malha tem seu osso `DEF-` como pai |
| 8 Hinges, 3 Slides, 1 Telescope | `CTRL-<part>` | Controles e sliders de **4. Controls** |
| 1 Piston | `MCH-<part>-aim` e `MCH-<part>-target` | Peças da escora apontam uma à outra |
| 1 Follow | nenhum | `PlateR` gira com `PlateL` |
| 2 Sequences | `CTRL-SEQ-<name>` | Um slider cada |
| 3 Forms | nenhum | Valores salvos dos sliders |

O exemplo atualizado passou Rig Validator sem problemas relatados, além de verificações de recarga com Auto Run Python Scripts desligado, incluindo todos os controles e as três Forms.

## Experimente depois

- Ative **Curve** em `PlateR Follow` e altere o mapeamento no Graph Editor.
- Salve uma quarta forma `Carry`, lâmina dobrada mas cabeça levantada.
- Anime formas em quadros com **Go and Key** e exporte ossos `DEF-` (veja [Ferramentas VRChat](08-vrchat.md)).

## Gear Link

Crescent Rose não tem par engrenado, portanto este rig não usa Gear Link. Ele gira uma Hinge a partir de outra pela razão de dentes: manivela/roda ou cremalheira que converte rotação em deslizamento. Veja [Gear Link](07-mechanisms.md#gear-link-ligação-de-engrenagem).

## Créditos

Modelo Crescent Rose por amandangm, https://sketchfab.com/3d-models/crescent-rose-dcb6bfbb3b824c01a182fa131fe35824, CC BY 4.0; separado, escalado e rigado para este tutorial. Crescent Rose é criação de Rooster Teeth Productions; este asset didático foi feito por fã.

[← Sumário](index.md)
