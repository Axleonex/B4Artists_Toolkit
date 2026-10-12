# Ferramentas do CATS

[← Conteúdo](index.md)

As ferramentas CATS estão na guia **CATS** na barra lateral direita (pressione**N**), na seção**CATS** e na guia**Properties** do editor**Scene** enquanto Preferências → Guias → Propriedades da cena → Mostrar está ativado. O switch da janela de visualização CATS e o switch Scene Properties controlam suas próprias cópias de forma independente. Eles seguem o pipeline descrito em [O gasoduto CATS](04-cats-pipeline.md). Escolha a armadura em que eles trabalham no topo da seção.

Na versão 9.1, vários painéis colocam configurações opcionais em uma dobra abaixo dos botões de ação. As entradas necessárias antes de executar uma ferramenta ainda vêm primeiro: corrigir as opções de limpeza do modelo, traduzir o idioma de origem dos nomes dos ossos e os formatos da boca ou dos ossos dos olhos. As ferramentas Bone que oferecem Adjust Last Operation são executadas imediatamente e permitem ajustar suas opções posteriormente. Passe o mouse sobre um botão ou opção para ler sua dica de ferramenta.

---

## Corrigir Modelo

**Fase do pipeline:** 1 (sempre primeiro)

**O que faz:** Uma limpeza com um clique antes de qualquer outra operação CATS. Ele remove problemas ocultos que, de outra forma, seriam interrompidos silenciosamente em cada etapa posterior.

**Opções (cada uma pode ser desativada):**
- Aplicar modificadores
- Remover duplicatas – mesclar vértices duplicados na mesma posição
- Recalcular normais – corrigir superfícies de dentro para fora
- Remover geometria solta — faces não anexadas ao corpo
- Remover grupos de vértices vazios
- Remova ossos de peso zero – ossos que não movem nenhum vértice
- Remover restrições e corpos rígidos VRChat não pode usar

Clique em **Fix Model** para executá-los na malha selecionada em uma passagem.

---

## Traduzir Nomes de Ossos

**O que faz:** Traduz os nomes dos ossos do seu esqueleto para nomes VRChat em inglês. Funciona offline, a partir de um dicionário integrado de nomes de ossos conhecidos.

**Idiomas suportados:** Japonês (日本語, o mais comum, de MMD e muitos modelos da comunidade), chinês (中文), coreano (한국어), português (Português), espanhol (Español) e francês (Français).

**Controles principais:** o**Language** dos nomes das fontes e o botão de tradução (**Translate Bone Names** ).

Trata-se do idioma dos nomes dos ossos do modelo, não do idioma da interface: para um modelo japonês MMD, use-o em qualquer idioma que Bforartists esteja definido.

---

## Unir Malhas

**O que faz:** Combina os objetos de malha do seu avatar em uma malha. VRChat tem melhor desempenho com uma malha por avatar. Quando as malhas têm chaves de forma diferentes, CATS preenche as que faltam com formas neutras, para que a malha unida tenha um conjunto consistente.

**Controles principais:** a lista de malhas (atualize-a com o botão próximo a ela) e depois**Join Meshes**.

**Quando usar:** depois de todas as roupas e acessórios estarem presos e pesados, e após Fix Model. A união antes do Fix Model espalha problemas de vértices duplicados de um objeto para outro; a malha unida mantém os vértices fantasmas de cada objeto original, e os visemas gerados separam-nos nas costuras.

---

## Combinador de atlas de materiais

**Fase do pipeline:** 2 (opcional)

**O que faz:** Coze vários materiais em uma folha de textura (um atlas). Menos materiais proporcionam uma melhor classificação de desempenho VRChat.

**Controles principais:**
- **Analyze** — lista seus materiais e texturas, com diagnósticos, grupos duplicados e substituições de tamanho. Escolha quais materiais e quais texturas incluir: desmarque aqueles que deseja manter como estão.
- **Smart Combine Materials** — o caminho recomendado: prepara o atlas e aponta cada malha para ele; o atlas UV torna-se UV0 para exportação
- **Bake Atlas** – um assado simples;**Add Group** e**Remove Group** assam grupos de materiais separadamente
- Substituir configurações herdadas - tamanho do atlas, método UV e semente, predefinição de empacotamento, preenchimento de cozimento, etapa de rotação da ilha e passagens de cozimento (Albedo por padrão; Normal, Emissão e Rugosidade podem ser cozidos como saídas separadas)
- **Preserve Backup Duplicate** — mantém uma cópia dos originais
- **Accept — Delete Backup** — mantém o resultado e exclui o backup
- **Revert — Restore Originals** — remonta aos materiais originais
- **Copy Debug Report** — copia o diagnóstico para a área de transferência para um relatório de bug

Os materiais VRM / MToon mantêm sua transparência: o modo alfa é respeitado e verificado em relação à textura alfa real, a emissão não explode e os blocos problemáticos são sinalizados em magenta após o cozimento.

**Créditos de linhagem:** este fluxo de trabalho continua a linhagem de integração CATS, credita o plug-in Cats Blender original, credita Grim-es/material-combiner-addon pela linhagem Material Combiner e credita UV Toolkit de Alexander Belyakov mais o repositório de arquivo oRazeD/UVToolkit para inspiração de fluxo de trabalho UV. BoneCraft implementa seus próprios auxiliares UV do atlas em vez de incluir a fonte UVToolkit.

---

## Visemas

**Fase de pipeline:** 3

**O que faz:** Cria os 15 visemas VRChat a partir de três formatos de boca básicos.

**Controles principais:** **A Shape**,**O Shape** e**CH Shape** (escolha-os ou**Auto-Detect** ) e depois**Generate Visemes**. Expanda Opções abaixo dos botões para escolher se deseja substituir os visemas existentes antes de gerar. Consulte [Guia 13, Fase 2](03-guides-b.md#fase-2--geração-de-visemas).

---

## Rastreamento Ocular

**Fase do pipeline:** 4 (executar após o modelo de correção)

Sem o Fix Model primeiro, a detecção de olhos pode se prender a sobras de geometria duplicada em vez dos olhos reais e colocar as restrições no espaço vazio – os avatares chegam em VRChat olhando para o chão.

**O que faz:** localiza os ossos dos olhos do seu avatar, nomeia-os conforme VRChat exige (`LeftEye` e `RightEye` ) e cria as restrições de rotação que movem os olhos naturalmente em VRChat.

**Controles principais:**
- **Auto-Detect** – encontra ossos que correspondem aos nomes e posições dos ossos do olho
- **Left Eye** e**Right Eye** – os ossos do olho, se você mesmo os escolher
- **Up Limit**,**Down Limit** e**Side Limit** – até onde os olhos podem virar
- **Create Eye Tracking** — renomeia os ossos e cria as restrições

---

## Pose e Shape Keys

**Fase de pipeline:** 5 (opcional)

### Pose para Shape Key

Transforma a pose atual em uma nova chave de forma — para expressões personalizadas ou uma forma de repouso corrigida. Posicione a armadura no modo Pose, retorne ao modo Object, clique em **Pose to Shape Key** e nomeie a chave de forma.

### Shape Key para Basis

O inverso: insere uma chave de forma na forma de repouso neutra da malha. Use-o para travar uma postura de descanso corrigida para sempre. Execute-o depois do Fix Model também.

---

## Transformes e FBT

**Fase do pipeline:** 6 (última)

### Aplicar Todos os Transformes

Aplica posição, rotação e escala à malha e à armadura juntas, para que tudo seja lido como valores limpos. O SDK VRChat precisa disso: a escala não aplicada torna os avatares do tamanho errado em VRChat.

### Corrigir FBT

Uma correção de transformação para configurações de Full Body Tracking: move o osso raiz para o nível do chão.

### Remover FBT

Remove a correção Fix FBT novamente.

---

## Ferramentas de Ossos

- **Create Root Bone** — adiciona um osso raiz (nomeado por**Root Name** ) na parte inferior da hierarquia
- **Merge Bones** — mescla ossos mais curtos que o**Merge Threshold** em seus pais
- **Duplicate Bones** — duplica os ossos selecionados

---

## Ferramentas de Armadura

**O que faz:** Mescla uma armadura com outra, por exemplo, a armadura de uma roupa com a do corpo.

**Controles principais:**
- **Base / Root** — a armadura que permanece (o resultado mantém seu nome)
- **Incoming** — a armadura que se funde nele; ossos com o mesmo nome dobram-se na base
- Naming Prep — faz com que os nomes dos ossos dos dois rigs correspondam antes da fusão. Funciona em qualquer rig, não apenas nas importações do Mixamo: escolha Mixamo Prefixed e clique em **Normalize Merge Names**, depois escolha Mixamo Stripped e normalize novamente; ambas as rigs terminam com os mesmos nomes.
- Opções para criar os ossos automaticamente e unir as malhas posteriormente
- **Merge Incoming Into Base** — mescla

Para uma mesclagem gradual com visualizações, use Bone Merge (consulte [Construtor de plataforma](06-rig-builder.md#mesclagem-de-ossos) ).

---

## Ferramentas de Malha

- **Separate by Materials** — uma malha por material
- **Separate by Loose Parts** — uma malha por peça conectada
- **Separate by Shape Keys** – divide as partes que moldam o movimento das teclas

---

## Smart Automatic Weights (pesos automáticos inteligentes)

**Smart Automatic Weights** abre uma caixa de diálogo: verifique a malha de destino e a armadura e escolha Corpo para recalcular a partir do rig existente ou Vestuário para transferir de uma malha de origem ponderada. A caixa de diálogo usa padrões inteligentes e mantém um backup oculto.**Advanced Recalculation** expande uma dica de localização para os controles completos em BoneCraft → Pele → Ferramentas de Peso; ele não abre esses controles aqui. Consulte [Ferramentas de plataforma](05-rig-tools.md#recálculo-automático-de-pesos-de-ossos).

---

## Status do Pipeline e Registro de Operações

O status do pipeline mostra quais das seis fases foram concluídas. O livro razão de operações lista cada operação CATS com seu tempo e resultado (alterado, limpo ou com falha); **Copy** coloca-o na área de transferência e**Clear** o esvazia. Consulte [O gasoduto CATS](04-cats-pipeline.md).

Próximo: [Correções rápidas e glossário](10-reference.md)
