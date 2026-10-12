# Soluções rápidas e glossário

[← Conteúdo](index.md)

## Índice de soluções rápidas

Use esta seção quando algo der errado e você precisar de uma resposta rápida.

|Problema|Onde procurar|
|---|---|
|Falha no upload — ossos não reconhecidos|[Guia 4](02-guides-a.md#guia-4-corrija-os-nomes-dos-ossos-do-seu-avatar) + [Extras de nomenclatura VRChat](08-vrchat.md#vrchat-naming-extras-extras-de-nomes-do-vrchat) |
|Avatar em pose T/não rastreia movimento|[Guia 5](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat) + [Configurar ossos humanóides](08-vrchat.md#configurar-ossos-humanóides) |
|Malha deformando-se estranhamente/estiramento da pele|[Transferência de peso](05-rig-tools.md#transferência-de-peso) + [Espelho de peso](05-rig-tools.md#espelho-de-peso) ou recalcular com [Recálculo automático do peso ósseo](05-rig-tools.md#recálculo-automático-de-pesos-de-ossos) |
|Um lado do corpo tem pesos diferentes|[Espelho de peso](05-rig-tools.md#espelho-de-peso) |
|Grampos de cabelo na cabeça|[Guia 6, Etapa 5](02-guides-a.md#passo-5--adicionar-colisores-recomendado) – adicionar colisores|
|A física do cabelo não se move|[Guia 6](02-guides-a.md#guia-6-adicione-física-de-cabelo) – verifique a detecção de cadeia e a predefinição PhysBone|
|Prendedores de roupas pelo corpo|[Guia 7](02-guides-a.md#guia-7-anexe-roupas-que-se-movem-com-seu-corpo) - execute **Detect Collisions** |
|A sincronização labial não funciona|[Guia 8](03-guides-b.md#guia-8-configure-a-sincronia-labial) + [VRChat Mapeamento de Visema](08-vrchat.md#vrchat-viseme-mapping-mapeamento-de-visemas-do-vrchat) |
|Avatar tem desempenho muito ruim|[Guia 9](03-guides-b.md#guia-9-melhore-o-desempenho-do-seu-avatar) + [Verifique o desempenho](08-vrchat.md#verificar-desempenho) |
|Falha na importação de VRM |[Guia 2, Etapa 1](02-guides-a.md#passo-1--instalar-o-add-on-vrm) — instale o complemento VRM |
|Falha na importação de MMD |[Guia 3, Etapa 1](02-guides-a.md#passo-1--instalar-o-mmd_tools) – instalar mmd_tools|
|O validador de rig mostra erros|[Validador de plataforma](05-rig-tools.md#validador-de-rig) — execute a validação e siga as mensagens|
|Ossos desapareceram / não consigo ver nenhum osso|[Coleções de Ossos](05-rig-tools.md#coleções-de-ossos) → **Show All Collections** |
|Não consigo encontrar os painéis de BoneCraft |BoneCraft e Rig Builder estão na prateleira de ferramentas esquerda (pressione T), CATS na barra lateral direita (pressione N) - consulte [Onde as coisas estão](01-start.md#onde-fica-cada-coisa) |
|Quero um exemplo completo de Mecanismos|[Tutorial: Crescent Rose](12-crescent-rose.md) — 8 etapas de preparação e 30 etapas de mecanismos com capturas de tela e o arquivo finalizado em `examples/crescent-rose/` |
|Uma guia está do lado errado|Preferências → Complementos → BoneCraft → Guias → Esquerda ou Direita|
|As seções de BoneCraft estão faltando em Propriedades → Cena|Preferências → Complementos → BoneCraft → Guias → Propriedades da cena → Mostrar; azul significa ligado. Verifique também os pacotes de ferramentas em Ferramentas|
|Quero ocultar BoneCraft em Propriedades → Cena|Desative Propriedades da cena → Mostrar em Preferências → Guias. Ele deixa as guias da janela de visualização e a guia de dados da armadura sozinhas|
|Uma ferramenta é executada antes que eu possa escolher suas opções|Na versão 9.1, ajuste suas opções imediatamente depois no painel Ajustar última operação da viewport, antes de executar outra operação|
|Colocar marcadores de rig não coloca um marcador|Inicie o Auto-Rig Wizard, vá para uma etapa do marcador, use o Object Mode e clique na malha selecionada do assistente - consulte [Construtor de plataforma](06-rig-builder.md#assistente-auto-rig) |
|O Build Mechanism não sabe quais peças usar|Adicione peças da seleção primeiro, selecione o rig do mecanismo ou uma de suas peças, escolha o tipo no cabeçalho da ferramenta e clique na primeira peça - consulte [Mecanismos](07-mechanisms.md#articulações-e-ligações-um-exemplo-de-cada) |
|Exportação bloqueada: ossos humanóides dados como desaparecidos, embora existam|Execute **Auto-Map All** e, em seguida,**Fix Humanoid Map** no lint da seção VRM / VRoid. Se um osso necessário realmente não existir, o rig precisa dele primeiro: consulte [Guia 5](02-guides-a.md#guia-5-mapeie-seu-avatar-para-o-sistema-corporal-do-vrchat) |
|FBX exportado mostra formas ou tubos auxiliares gigantes|Mantenha **Helper Meshes** desligado, a menos que você precise de controle ou malhas de formato personalizado|
|Unity ou Unreal importa materiais cinzentos|Exporte com **Embed Textures** ativado e, em seguida, use as opções de importação/extração de material do Unity ou a importação de material FBX do Unreal|
|Os pesos estão todos nos ossos errados|Execute novamente o assistente Generate Rig, use [Transferência de peso](05-rig-tools.md#transferência-de-peso) ou **Smart Automatic Weights** na guia CATS |
|Duas rigs precisam ser uma|[Guia 11: Mesclar duas plataformas](03-guides-b.md#guia-11-junte-dois-rigs) |
|Forma corretiva não liga|Verifique o eixo e o ângulo do osso em [Chaves de forma corretivas](05-rig-tools.md#shape-keys-corretivos) |
|A animação parece errada em um rig diferente|[Redirecionar](05-rig-tools.md#redirecionar) — verifique o mapeamento ósseo|
|Uma ferramenta CATS avisa "Execute o modelo de correção primeiro"|Executar modelo de correção — [O gasoduto CATS](04-cats-pipeline.md) |
|A boca se rasga ou se divide ao falar|O modelo de correção foi ignorado — execute novamente a partir da Fase 1 — [Guia 13, Fase 1](03-guides-b.md#fase-1--corrigir-modelo) |
|Os olhos do Avatar ficaram olhando para baixo em VRChat |O rastreamento ocular foi executado antes do modelo de correção - executado novamente a partir do modelo de correção - [CATS: rastreamento ocular](09-cats.md#rastreamento-ocular) |
|Shape key faz a malha explodir quando acionada|Pose to Shape Key foi executado antes do modelo de correção - executado novamente a partir do modelo de correção - [CATS: Chaves de pose e forma](09-cats.md#pose-e-shape-keys) |
|O avatar aparece no tamanho errado em VRChat |As transformações foram aplicadas antes da conclusão do pipeline – reimporte do arquivo de origem e reinicie do Fix Model|
|Os nomes dos ossos são japoneses/chineses/coreanos|[CATS: Traduzir nomes de ossos](09-cats.md#traduzir-nomes-de-ossos) |
|Avatar não tem sincronização labial nem teclas de formato de boca|[CATS: Visemas](09-cats.md#visemas) — gera 15 visemas a partir de 3 formatos de base|
|Um mecanismo mostra "alterado manualmente"|[Mecanismos](07-mechanisms.md) — use **Keep mine** ou**Restore** |

## Glossário

**Ajustar última operação:** O painel da janela de visualização para alterar as opções da operação que você acabou de executar. Muitas ferramentas BoneCraft 9.1 são executadas primeiro e apresentam suas opções aqui; ajuste-os antes de executar outra operação.

**Armature:** Bforartists ' palavra para esqueleto: um conjunto de ossos que podem ser colocados e animados.

**Forma de mesclagem:** Consulte Chave de forma.

**Osso:** Um segmento de um esqueleto. Os ossos formam uma hierarquia (pai → filho) na qual os ossos filhos seguem seus pais.

**Coleção de ossos:** Um grupo nomeado de ossos. Você pode mostrar ou ocultar uma coleção inteira de uma só vez.

**CATS:** As ferramentas CATS: preparação de modelo para VRChat com um pipeline guiado (limpeza, visemas, rastreamento ocular, transformações). Eles estão na guia CATS.

**Tubulação CATS:** A ordem de seis fases das ferramentas CATS: Fix Model → Material Atlas → Visemes → Eye Tracking → Pose to Shape → Apply Transforms. As ferramentas avisam quando uma fase anterior da qual dependem não foi concluída.

**Chave de forma corretiva:** uma chave de forma que é ativada quando um osso atinge um ângulo, para corrigir a malha em poses extremas.

**Deformar osso:** Um osso que move a malha. Nem todo osso se deforma; alguns são apenas controles.

**Rastreamento ocular:** a ferramenta CATS que configura os ossos oculares (`LeftEye`, `RightEye` ) e as restrições de rotação que VRChat usa para mover os olhos.

**FBT (Full Body Tracking):** Um recurso VRChat que rastreia todo o seu corpo com hardware extra (como Vive Trackers), incluindo quadris e pés. Fix FBT ajusta o osso da raiz para isso.

**FBX:** Um formato de arquivo que transporta modelos 3D, esqueletos e animações entre programas. O formato padrão para VRChat.

**Modelo de correção:** A limpeza CATS: vértices duplicados, geometria solta e normais ruins. Sempre o primeiro passo CATS.

**FK (Cinemática direta):** Posar girando cada osso de uma corrente por vez: ombro, depois cotovelo e depois punho. Natural para poses de corpo largo.

**IK (Cinemática Inversa):** Posar colocando a ponta de uma corrente (uma mão ou um pé); os ossos intermediários seguem. Natural para posicionamento preciso das mãos e dos pés.

**Humanóide:** sistema de avatar de VRChat que mapeia ossos para slots corporais padrão, de modo que cada avatar usa os mesmos controles de movimento.

**Mecanismo:** Um rig para um suporte ou peça de máquina: uma junta (dobradiça, corrediça, telescópio) ou um elo (pistão, elo de engrenagem, seguimento), construído a partir de ossos e restrições comuns. Consulte [Mecanismos](07-mechanisms.md).

**Malha:** a superfície 3D que compõe o corpo visível do seu avatar.

**MMD (MikuMikuDance):** Software de animação 3D gratuito, popular no Japão e na comunidade de anime. Usa arquivos de modelo `.pmx` e arquivos de animação `.vmd`.

**Alvo de transformação:** Consulte Chave de forma.

**Ledger de operações:** a lista CATS de todas as operações que você executou, com seu tempo e resultado.

**PhysBone:** Componente do VRChat que faz os ossos balançarem, saltarem e colidirem. Usado para cabelos, caudas e acessórios pendurados.

**Status do pipeline:** A lista CATS das seis fases, com uma marca de seleção para cada fase concluída.

**PMX:** Formato principal do modelo 3D do MikuMikuDance.

**Modo Pose:** O modo para posicionar e animar ossos. Selecione a armadura e pressione Ctrl+Tab ou use o menu suspenso de modo no canto superior esquerdo da janela de visualização.

**Rig / rigging:** Construir um esqueleto dentro de um modelo 3D e conectar a malha a ele para que possa ser posado e animado.

**Chave de forma:** uma versão salva de uma malha em uma posição deformada. As chaves de forma se misturam em diferentes intensidades; eles conduzem expressões faciais, sincronização labial e formas corporais.

**SDK (Kit de desenvolvimento de software):** Para VRChat, o VRChat Creator Companion e suas ferramentas Unity para upload de avatares.

**Spline IK:** Uma cadeia de ossos que segue uma curva. Usado para caudas, tentáculos, cabelos longos e espinhos.

**T-pose:** Uma pose de referência: ficar em pé com os braços estendidos para os lados.

**Prateleira de ferramentas:** O painel no lado esquerdo da janela de visualização 3D (pressione T), onde as guias BoneCraft e Rig Builder estão por padrão.

**Vértice:** Um único ponto no espaço 3D. As malhas são feitas de muitos vértices unidos por arestas e faces.

**Grupo de vértices:** Um conjunto nomeado de vértices; ele define quais vértices um osso se move.

**Visema:** formato de boca para um som de fala. VRChat usa 15 visemas para sincronização labial.

**Pintura de peso/peso:** Valores de 0,0 a 1,0 que dizem a força com que cada osso move cada vértice. A pintura de peso é a forma visual de ajustá-los.

**Assistente:** O Assistente Auto-Rig do Rig Builder: coloca marcadores em sua malha e constrói o rig a partir deles.

**Osso de peso zero:** Um osso que não move nenhum vértice. Custa desempenho sem alterar a aparência do avatar; Fix Model e o otimizador de desempenho os removem.

Próximo: [Novidades](11-whats-new.md)
