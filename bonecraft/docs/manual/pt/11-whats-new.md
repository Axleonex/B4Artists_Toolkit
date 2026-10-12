# Novidades

[← Conteúdo](index.md)

O mais novo primeiro.

## 9.1.2 (outubro de 2026)

- **Alteração Propriedades da cena:** Preferências > Guias tem uma nova linha Propriedades da cena. Seu botão Mostrar (azul enquanto ativado) mostra ou oculta todas as seções de BoneCraft em Propriedades> guia Cena (Rig Builder, Mecanismos, CATS, Ferramentas de Avatar, Ferramentas VRChat, Importação/Exportação) sem desabilitar o complemento. Ele inicia e deixa as guias da janela de visualização e a guia Armadura sozinhas. Consulte [Onde as coisas estão](01-start.md#onde-fica-cada-coisa).

## 9.1.1 (outubro de 2026)

- **Ícones mais claros:** cada ícone agora significa uma coisa em todos os lugares. Cerca de 60 botões obtiveram um ícone Bforartists mais adequado (por exemplo, Aplicar todas as transformações, Dizimar, Normalizar nomes, Traduzir, Mesclar, Separar, Misturar pose e Sincronização labial) e um botão mostra o mesmo ícone em cada painel.
- **Painéis mais calmos:** títulos e texto fixo não carregam mais ícones de tópico. As dicas que relatam um estado mostram o ícone de informação, aviso ou verificação.
- **Grade de ícones legíveis:** cada botão nas guias da Prateleira de ferramentas Pose e Pesos tem seu próprio ícone, portanto, uma prateleira estreita permanece legível.

## 9.1.0 (outubro de 2026)

- **Ferramentas onde Bforartists se destaca:** Entradas BoneCraft nos menus Adicionar → Armadura, Pose, Pesos e Objeto, e um painel de botões BoneCraft nas guias da Prateleira de ferramentas Pose e Pesos do Bforartists.
- **Aja primeiro, ajuste depois:** Quick Rig, Fit Dropped Rig, as ferramentas de peso, Ribbon, Spline IK, Delta Mush e as ferramentas ósseas CATS são executadas de uma só vez com os valores que você usou pela última vez; você os ajusta posteriormente no painel Ajustar última operação. Menos pop-ups do tipo “você tem certeza”.
- **Ações primeiro, opções dobradas:** vários painéis mostram seus botões primeiro e configurações opcionais em uma dobra abaixo. As entradas necessárias permanecem antes da ação, assim como as opções de limpeza do Fix Model. As configurações se parecem com configurações (caixas de seleção, nunca botões) e os cabeçalhos dos painéis não possuem ícones.
- **Ferramentas de gestos:** Place Rig Markers (clique na malha para posicionar o próximo marcador do Auto-Rig Wizard) e Build Mechanism (clique em uma peça para iniciar uma junta ou link) estão na barra de ferramentas da viewport.
- **Seções de avatar:** Ferramentas de Avatar contêm mapeamento humanóide, cabelo, visemas e exportação. A seção separada de Ferramentas VRChat agrupa utilitários de Desempenho, Vestuário e Nomenclatura. Os guias usam esses nomes de painel atuais.
- **Dicas:** cada operador e cada opção se explicam.
- **Mostre, não esconda:** as seções permanecem visíveis e dizem o que selecionar quando o rig for removido, o Auto-Rig Wizard vem primeiro no Rig Builder e as prateleiras começam largas o suficiente para serem lidas.
- **Fixes:** Gerar Spline IK funciona novamente; Adicionar Influência usa o osso escolhido; as visualizações do visema usam seu conjunto.

## 9.0.0 (outubro de 2026)

- **Mecanismos:** uma nova seção da guia BoneCraft (e da guia Cena de Propriedades) que monta acessórios e máquinas: Dobradiça, Corrediça, Telescópio, Pistão, Elo de Engrenagem, Acompanhamento e Sequência, construídos com etapas guiadas e verificados com Teste. BoneCraft nunca substitui uma edição manual: você escolhe**Keep mine** para mantê-la ou**Restore** para reconstruir. Consulte [Mecanismos](07-mechanisms.md).
- **Arquivo de exemplo:** `examples/crescent-rose/` contém Crescent Rose equipado com mecanismos (foice, rifle e formas compactas), e o [capítulo 12](12-crescent-rose.md) do manual o constrói passo a passo.
- **Lados das guias:** cada guia da janela de visualização pode ficar na prateleira de ferramentas esquerda ou na barra lateral direita (Preferências → Guias → Esquerda/Direita). BoneCraft e Rig Builder começam à esquerda, CATS à direita.
- **Rig Builder:** sempre na guia Cena de propriedades, além de sua própria guia de viewport com um layout compacto para uma prateleira de ferramentas estreita. Uma rig Basic Humanoid é fornecida na biblioteca de ativos BoneCraft Rigs; Fit Dropped Rig cabe em um rig retirado da prateleira de ativos.
- **Guia CATS:** Importação/Exportação movida para a guia CATS. CATS, VRChat e Importação/Exportação também estão sempre na guia Cena.
- **Mostrar Auxiliares:** uma preferência mostra ou oculta o texto didático de BoneCraft; O Modo Compacto é o seu atalho.
- **Validador de plataforma:** nomes de ossos com hífens passam; os drivers avisam apenas para expressões que precisam de Python; As rigs de mecanismos também são verificadas. A tarefa do validador do Task Board reporta novamente.
- **Nome:** o complemento se chama BoneCraft.

## 8.9.x (setembro–outubro de 2026)

- **8.9.6:** toda a peça do vestido segue os ossos da saia (sem recorte no quadril); corretivos de canto de mandíbula aberta com lábios pegajosos.
- **8.9.5:** IK/FK interruptor de cotovelo sem estalo; detecção simétrica de ombros; os marcadores oculares não quebram mais; o Seletor de Controle mostra a seleção; cantos da boca mais arredondados; uma correção do vestido sobre a coxa; clavículas relaxadas; Exportação em T.
- **8.9.4:** joelhos mais arredondados (corretivos substituem Preservar Volume); chaves de contato para curvas profundas; uma mistura de costura nos ombros.
- **8.9.3:** ossos da saia de dois segmentos que seguem e são empurrados pelas pernas.
- **8.9.2:** pisca com chaves de forma (sem dobras na tampa); uma abertura de boca oval.
- **8.9.1:** skin muito mais rápido em malhas densas (678.000 vértices: 232 sa 57 s); calor ósseo através de uma malha proxy mais leve, em vez de falhar silenciosamente.
- **8.9.0:** chaves de forma corretivas de juntas; controles de rosto (mirar os olhos, piscar, seguir os lábios); roupas que dobram com as juntas.
- Também no 8.9: recálculo automático do peso ósseo e uma seleção de atlas mais clara.

## 8.7–8.8 (setembro de 2026)

- **8.8.0:** o painel de redirecionamento funciona em hosts Blender 5; marcadores de dedos colocados a partir do formato da mão; IK estiramento na pele; uma opção Preservar Volume; uma correção de ligação Delta Mush.
- **8.7.0:** um rig de controle integrado; detecção de articulações traçadas em membros; redirecionamento de direção correspondente; torcer os ossos.

## 8.5–8.6 (julho de 2026)

- **8.6.1–8.6.3:** Atlas de materiais: diagnóstico de ladrilhos após cozimento; A transparência do MToon é verificada em relação à textura alfa real e mantida durante o atlas; melhor particionamento de materiais mistos.
- **8.5.5–8.5.10:** Materiais VRM / MToon: o modo alfa é respeitado, alfa funciona em hosts Blender 5, sem explosão de emissão, diagnóstico magenta e nomes de atlas seguros.
- **8.5.4:** o mapeamento humanóide é lido corretamente; Orientação para preparação de nomenclatura.
- **8.5.2–8.5.3:** importe um download VRoid (.zip); um cartão de transferência de projeto VRoid.
- **8.5.1:** Exportação FBX que mantém formas mescladas.

## Versões anteriores

**8.5.0:** O Smart Combine agora torna `atlas_uv` o UV0 de exportação por padrão após o cozimento. O mapa UV de origem do pré-atlas é removido da malha do atlas gerada, a menos que**Keep Source UV Maps** esteja habilitado em Configurações avançadas. Os controles derivados de CATS / Material Combiner / UVToolkit agora são compartilhados com a construção aberta Blender; A exclusividade da B4Artists permanece nos sistemas de rigging de produção, controle, redirecionamento/exportação e lançamento exclusivo da B4Artists.

A versão 8.5.0 também atualiza o fluxo de trabalho de exportação e validação. As exportações VRChat, VRM, MMD e Unreal agora expõem controles de pasta e nome de arquivo nos painéis BoneCraft em vez de forçá-lo a confiar apenas nos padrões do navegador de arquivos de Blender. As exportações VRChat /Unity e Unreal FBX são padronizadas como **Embed Textures** para facilitar a importação de material, enquanto a exportação VRChat mantém malhas auxiliares/forma de controle fora do FBX, a menos que**Helper Meshes** está ativado. O painel VRM agora inclui**Lint Now** mais**Fix Humanoid Map**, que pode reparar o mapeamento de alias humanóide obsoleto antes da exportação sem renomear seus ossos.

**8.4.5:** O Smart Combine agora força as texturas de origem a amostrarem o UV pré-atlas preservado durante o cozimento, valida a malha do atlas gerada antes de ocultar os originais e redefine todas as faces do atlas para o slot de material do atlas final para evitar pedaços de manto/roupa cinza ou embaralhados.

**8.4.4:** O Material Atlas Combiner adiciona controles de inspeção de paridade de qualidade antes do cozimento: diagnóstico de shader/material, rótulos de função de textura, marcadores de origem duplicados/compartilhados, substituições de tamanho por material, predefinições de empacotamento, cozimentos opcionais de saída Normal/Emissão/Rugosidade e bloqueadores de preflight para empacotamento de canal metálico/ORM até que esse caminho seja verificado.

**8.4.3:** O Material Atlas Combiner inclui métodos de embalagem UV selecionáveis dentro do fluxo de trabalho existente do Material Atlas. Inclui Smart Pack, Grid Pack, Seeed Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation e Rotation Step, com detalhes do método UV registrados no relatório de depuração e no registro de cozimento.

**8.4.2:** O Material Atlas Combiner agora tem como alvo o UV do atlas gerado durante o cozimento, enquanto os nós de textura de origem copiados leem explicitamente o UV do pré-atlas. Isso corrige resultados quebrados de atlas de mantos/roupas causados por texturas de origem e o atlas cozido amostrando diferentes mapas UV. As linhas selecionáveis de material e textura da versão 8.4.1 permanecem disponíveis.

**7.1.3 (limpeza do rótulo de preferência):** Duas opções de alternância de preferências complementares foram renomeadas para que agora correspondam à guia da barra lateral que controlam. "VRChat Avatar Tools" agora é rotulado como**CATS** (corresponde à guia da barra lateral CATS ). "Task Board & Sidebar" agora é rotulado como**Rig Builder** (corresponde à guia da barra lateral do Rig Builder). Nenhuma ferramenta foi removida – apenas os rótulos de ativação/desativação em Editar > Preferências > Complementos > BoneCraft foram alterados.

**7.1.1:** BoneCraft agora inclui as ferramentas CATS — um conjunto completo de ferramentas de preparação de modelo projetadas especificamente para deixar os avatares VRChat limpos, otimizados e totalmente configurados. CATS reside em sua própria guia na barra lateral e usa um sistema de pipeline que sempre o orienta pela ordem correta de operações.

Próximo: [Tutorial: Crescent Rose com mecanismos](12-crescent-rose.md)
