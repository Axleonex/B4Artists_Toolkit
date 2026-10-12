# Soluções rápidas e glossário

[← Sumário](index.md)

## Índice de soluções rápidas

Use esta seção quando algo der errado e você precisar da resposta rápido.

| Problema | Onde olhar |
|---|---|
| O envio falha — ossos não reconhecidos | [Guia 4](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar) + [VRChat Naming Extras](08-vrchat.md#vrchat-naming-extras-extras-de-nomes-do-vrchat) |
| Avatar em pose T / não acompanha o movimento | [Guia 5](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat) + [Configurar Ossos Humanóides](08-vrchat.md#configurar-ossos-humanóides) |
| A malha se deforma de um jeito estranho / a pele estica | [Transferência de peso](05-rig-tools.md#transferência-de-peso) + [Espelho de Peso](05-rig-tools.md#espelho-de-peso), ou recalcule com o [Recálculo automático de pesos de ossos](05-rig-tools.md#recálculo-automático-de-pesos-de-ossos) |
| Um lado do corpo tem pesos diferentes | [Espelho de Peso](05-rig-tools.md#espelho-de-peso) |
| O cabelo atravessa a cabeça | [Guia 6, passo 5](02-guides-a.md#passo-5--adicionar-colisores-recomendado) — adicione colisores |
| A física do cabelo não se mexe | [Guia 6](02-guides-a.md#guia-6-adicione-física-de-cabelo) — confira a detecção de cadeias e o preset de PhysBone |
| A roupa atravessa o corpo | [Guia 7](02-guides-a.md#guia-7-anexe-roupas-que-se-movem-com-seu-corpo) — execute **Detectar colisões** |
| A sincronia labial não funciona | [Guia 8](03-guides-b.md#guia-8-configure-a-sincronia-labial) + [VRChat Viseme Mapping](08-vrchat.md#vrchat-viseme-mapping-mapeamento-de-visemas-do-vrchat) |
| O avatar tem desempenho Very Poor | [Guia 9](03-guides-b.md#guia-9-melhore-o-desempenho-do-seu-avatar) + [Verificar Desempenho](08-vrchat.md#verificar-desempenho) |
| A importação de VRM falha | [Guia 2, passo 1](02-guides-a.md#passo-1--instalar-o-add-on-vrm) — instale o add-on VRM |
| A importação de MMD falha | [Guia 3, passo 1](02-guides-a.md#passo-1--instalar-o-mmd_tools) — instale o mmd_tools |
| O validador de rig mostra erros | [Validador de Rig](05-rig-tools.md#validador-de-rig) — execute a validação e siga as mensagens |
| Os ossos sumiram / não dá para ver nenhum osso | [Coleções de ossos](05-rig-tools.md#coleções-de-ossos) → **Show All Collections** (mostrar todas as coleções) |
| Não encontra os painéis do BoneCraft | BoneCraft e Rig Builder ficam na Tool Shelf da esquerda (pressione T), CATS na barra lateral da direita (pressione N) — veja [Onde fica cada coisa](01-start.md#onde-fica-cada-coisa) |
| Uma aba está do lado errado | Preferências → Add-ons → BoneCraft → Tabs → Left (esquerda) ou Right (direita) |
| Exportação bloqueada: ossos humanoides informados como ausentes embora existam | Execute **Mapear Tudo Automaticamente** e depois **Fix Humanoid Map** (corrigir mapa humanoide) na verificação da seção VRM / VRoid. Se um osso obrigatório realmente não existe, o rig precisa tê-lo primeiro: veja o [guia 5](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat) |
| O FBX exportado mostra formas auxiliares ou tubos gigantes | Deixe **Helper Meshes** (malhas auxiliares) desativado, a menos que você precise de malhas de controle ou de formas personalizadas |
| O Unity ou o Unreal importam materiais cinza | Exporte com **Embed Textures** (incorporar texturas) ativado e depois use as opções de importação/extração de materiais do Unity ou a importação de materiais FBX do Unreal |
| Os pesos estão todos nos ossos errados | Execute de novo **Gerar rig** do assistente, use a [Transferência de peso](05-rig-tools.md#transferência-de-peso), ou **Smart Automatic Weights** (pesos automáticos inteligentes) na aba CATS |
| Dois rigs precisam virar um | [Guia 11: junte dois rigs](03-guides-b.md#guia-11-junte-dois-rigs) |
| Uma forma corretiva não liga | Confira o eixo do osso e o ângulo em [Shape keys corretivos](05-rig-tools.md#shape-keys-corretivos) |
| A animação fica errada em outro rig | [Redirecionar](05-rig-tools.md#redirecionar) — confira o mapeamento de ossos |
| Uma ferramenta do CATS avisa "Run Fix Model first" | Execute **Corrigir Modelo** — [O pipeline do CATS](04-cats-pipeline.md) |
| A boca rasga ou se parte ao falar | **Corrigir Modelo** foi pulado — execute de novo a partir da fase 1 — [Guia 13, fase 1](03-guides-b.md#fase-1--corrigir-modelo) |
| Os olhos do avatar ficam travados olhando para baixo no VRChat | O rastreamento ocular foi executado antes de **Corrigir Modelo** — execute de novo a partir de **Corrigir Modelo** — [CATS: Rastreamento Ocular](09-cats.md#rastreamento-ocular) |
| Um shape key faz a malha explodir quando acionado | **Pose para Shape Key** foi executado antes de **Corrigir Modelo** — execute de novo a partir de **Corrigir Modelo** — [CATS: Pose e Shape Keys](09-cats.md#pose-e-shape-keys) |
| O avatar aparece com o tamanho errado no VRChat | As transformações foram aplicadas antes de o pipeline terminar — reimporte do arquivo de origem e recomece em **Corrigir Modelo** |
| Os nomes dos ossos estão em japonês / chinês / coreano | [CATS: Traduzir Nomes de Ossos](09-cats.md#traduzir-nomes-de-ossos) |
| O avatar não tem sincronia labial nem shape keys de boca | [CATS: Visemas](09-cats.md#visemas) — gere 15 visemas a partir de 3 formas base |
| Um mecanismo mostra "changed by hand" | [Mechanisms (mecanismos)](07-mechanisms.md) — use **Keep mine** (manter o meu) ou **Restaurar** |

## Glossário

**Armadura (Armature):** a palavra do Bforartists para um esqueleto: um conjunto de ossos que pode receber poses e ser animado.

**Blend shape:** veja Shape key.

**Osso (Bone):** um segmento de um esqueleto. Os ossos formam uma hierarquia (pai → filho) em que os ossos filhos seguem os pais.

**Coleção de ossos (Bone collection):** um grupo de ossos com nome. Você pode mostrar ou ocultar uma coleção inteira de uma vez.

**CATS:** as ferramentas do CATS: preparação de modelos para o VRChat com um pipeline guiado (limpeza, visemas, rastreamento ocular, transformações). Elas ficam na aba CATS.

**Pipeline do CATS (CATS pipeline):** a ordem em seis fases das ferramentas do CATS: Corrigir Modelo → Atlas de Materiais → Visemas → Rastreamento Ocular → Pose para Shape Key → Aplicar transformações. As ferramentas avisam quando uma fase anterior da qual dependem não foi feita.

**Shape key corretivo (Corrective shape key):** um shape key que liga quando um osso atinge um ângulo, para corrigir a malha em poses extremas.

**Osso de deformação (Deform bone):** um osso que move a malha. Nem todo osso deforma; alguns são só controles.

**Rastreamento ocular (Eye tracking):** a ferramenta do CATS que configura os ossos dos olhos (`LeftEye`, `RightEye`) e as restrições de rotação que o VRChat usa para mover os olhos.

**FBT (Full Body Tracking):** um recurso do VRChat que rastreia o corpo inteiro com hardware extra (como Vive Trackers), incluindo quadril e pés. **Corrigir FBT** ajusta o osso raiz para isso.

**FBX:** um formato de arquivo que leva modelos 3D, esqueletos e animações entre programas. O formato padrão para o VRChat.

**Corrigir Modelo (Fix Model):** a limpeza do CATS: vértices duplicados, geometria solta e normais erradas. Sempre o primeiro passo do CATS.

**FK (cinemática direta, Forward Kinematics):** fazer a pose girando cada osso de uma cadeia por vez: ombro, depois cotovelo, depois pulso. Natural para poses amplas do corpo.

**IK (cinemática inversa, Inverse Kinematics):** fazer a pose posicionando a ponta de uma cadeia (uma mão ou um pé); os ossos do meio acompanham. Natural para posicionar mãos e pés com precisão.

**Humanoide (Humanoid):** o sistema de avatares do VRChat que mapeia os ossos para slots padrão do corpo, para que todo avatar use os mesmos controles de movimento.

**Mecanismo (Mechanism):** um rig para um acessório ou uma peça de máquina: uma articulação (Hinge, Slide, Telescope) ou uma ligação (Piston, Gear Link, Follow), construída com ossos e restrições comuns. Veja [Mechanisms (mecanismos)](07-mechanisms.md).

**Malha (Mesh):** a superfície 3D que forma o corpo visível do seu avatar.

**MMD (MikuMikuDance):** um software gratuito de animação 3D popular no Japão e na comunidade de anime. Usa arquivos de modelo `.pmx` e arquivos de animação `.vmd`.

**Morph target:** veja Shape key.

**Registro de Operações (Operation Ledger):** a lista do CATS com cada operação que você executou, com a hora e o resultado.

**PhysBone:** o componente do VRChat que faz os ossos balançarem, quicarem e colidirem. Usado em cabelo, caudas e acessórios pendurados.

**Status do Pipeline (Pipeline Status):** a lista do CATS com as seis fases, com uma marca em cada fase concluída.

**PMX:** o principal formato de modelo 3D do MikuMikuDance.

**Modo Pose (Pose Mode):** o modo para fazer poses e animar ossos. Selecione a armadura e pressione Ctrl+Tab, ou use o menu suspenso de modos no canto superior esquerdo da viewport.

**Rig / rigging:** construir um esqueleto dentro de um modelo 3D e ligar a malha a ele para que possa receber poses e ser animado.

**Shape key:** uma versão salva de uma malha em uma posição deformada. Os shape keys se misturam em intensidades diferentes; eles movimentam expressões faciais, sincronia labial e mudanças de forma do corpo.

**SDK (Software Development Kit):** no VRChat, o VRChat Creator Companion e suas ferramentas do Unity para enviar avatares.

**Spline IK:** uma cadeia de ossos que segue uma curva. Usada em caudas, tentáculos, cabelos longos e colunas.

**Pose T (T-pose):** uma pose de referência: em pé, com os braços estendidos para os lados.

**Tool Shelf:** o painel do lado esquerdo da viewport 3D (pressione T), onde ficam por padrão as abas BoneCraft e Rig Builder.

**Vértice (Vertex):** um único ponto no espaço 3D. As malhas são feitas de muitos vértices ligados por arestas e faces.

**Grupo de vértices (Vertex group):** um conjunto de vértices com nome; define quais vértices um osso move.

**Visema (Viseme):** uma forma de boca para um som da fala. O VRChat usa 15 visemas para a sincronia labial.

**Peso / pintura de pesos (Weight / weight painting):** valores de 0.0 a 1.0 que dizem com que força cada osso move cada vértice. A pintura de pesos é o jeito visual de ajustá-los.

**Assistente (Wizard):** o Assistente Auto-Rig do Construtor de Rig: posiciona marcadores na sua malha e constrói o rig a partir deles.

**Osso de peso zero (Zero-weight bone):** um osso que não move nenhum vértice. Ele custa desempenho sem mudar a aparência do avatar; **Corrigir Modelo** e o otimizador de desempenho os removem.

Próximo: [Novidades](11-whats-new.md)
