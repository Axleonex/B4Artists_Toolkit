# Novidades

[← Sumário](index.md)

O mais recente primeiro.

## 9.2.5 — Aba do catálogo Starter Rigs

Starter Rigs agora usa uma aba única na prateleira nativa de assets inferior. Os controles superiores esquerdos da viewport foram removidos. Ative **Starter Rigs** uma vez no menu de catálogos para mostrar sua aba ao lado das outras. Importação nativa e **Add → Armature → Starter Rig Catalog** continuam disponíveis.

## 9.2.4 — Quadro de Tarefas e ferramentas nativas

**Abrir verificação de saúde** agora executa a validação do rig e abre os resultados. Selecione uma armature ou sua malha vinculada. **Quick Wins** mostra até três recomendações; **Remaining Tasks** não repete esses cartões. **Atualizar Quadro de Tarefas** verifica novamente.

Place Rig Markers e Build Mechanism continuam disponíveis como ferramentas da viewport. Seu registro não interfere mais no Grab/Move nativo nem na alternância cíclica de ferramentas nos modos Objeto e Pose.

## 9.2.3 — Local da exportação VRChat

Remove o painel duplicado Export to VRChat de Avatar Tools. A exportação permanece em CATS → Import / Export → Unity / VRChat.

## 9.2.2 — Interface atual

As abas selecionam grupos de ferramentas. Setup Rigging, Skin, Review, Avatar Tools e Facial são seções expansíveis dentro das abas, não abas separadas. Os caminhos abaixo usam os nomes da interface em inglês; a tradução depende de Language.

- Bone Merge → BoneCraft → Setup Rigging
- Delta Mush / Proximity Wrap → BoneCraft → Skin
- Viseme Library / Lip Sync → CATS → Avatar Tools
- VRChat Viseme Mapping / Face Tracking → CATS → VRChat Tools → Facial

## 9.2.0 (outubro de 2026)

- **Catálogo completo:** nove esqueletos/metarigs em miniaturas: Basic Humanoid, Simple Human, Full Human, Basic Quadruped, Cat, Horse, Wolf, Bird, Shark. Grupos Humans, Quadrupeds e Other Animals.
- **Rigify quando necessário:** Basic Humanoid é independente. Os demais continuam visíveis com Rigify desligado; escolher oferece **Enable Rigify & Add Rig** ou Cancel. Cancelamento, falha de ativação ou preset ausente não adicionam nada.
- **Prateleira opcional naquela versão:** a chave **Starter Rigs** no cabeçalho voltava à prateleira regular; escolha persistia nas preferências. **Add → Armature → Starter Rig Catalog** abria o seletor pop-up.
- **Clique ou arraste:** clique adiciona; solte na viewport. Adaptação à malha ligada, pesos e controles desligados; ajuste em Adjust Last Operation. Clique, arraste, cancelamento e desfazer/refazer nativos verificados em Bforartists 5.2.0.

## 9.1.2 (outubro de 2026)

- **Chave Propriedades da cena:** Preferências > Abas tem uma nova linha Propriedades da cena. Seu botão Mostrar (azul enquanto ligado) mostra ou oculta todas as seções do BoneCraft em Propriedades > aba Cena (Construtor de Rig, Mecanismos, CATS, VRChat, Importar / Exportar) sem desativar o complemento. Começa ligado e não altera as abas da janela 3D nem a aba Armadura.

## 9.1.1 (outubro de 2026)

- **Ícones mais claros:** cada ícone agora significa uma só coisa em todo lugar. Cerca de 60 botões ganharam um ícone do Bforartists mais adequado (por exemplo Aplicar todas as transformações, Decimar, Normalizar nomes, Traduzir, Mesclar, Separar, Misturar pose e Sincronia labial), e um botão mostra o mesmo ícone em todos os painéis.
- **Painéis mais calmos:** títulos e textos fixos não têm mais ícones de tema. Avisos que informam um estado mostram o ícone de informação, de aviso ou de confirmação.
- **Grade de ícones legível:** cada botão das abas Pose e Pesos da barra de ferramentas tem seu próprio ícone, então uma barra estreita continua legível.

## 9.1.0 (outubro de 2026)

- **Ferramentas onde o Bforartists põe as suas:** entradas do BoneCraft nos menus Adicionar → Armadura, Pose, Pesos e Objeto, e um painel de botões do BoneCraft nas abas Pose e Pesos da barra de ferramentas do Bforartists.
- **Primeiro agir, depois ajustar:** Rig rápido, Ajustar rig solto, as ferramentas de pesos, Fita, Spline IK, Delta Mush e as ferramentas de ossos do CATS executam na hora com os últimos valores usados; você os ajusta depois no painel Ajustar última operação. Menos janelas de "tem certeza?".
- **Ações primeiro, opções recolhidas:** os painéis mostram primeiro os botões e as configurações numa área recolhida abaixo. Configurações parecem configurações (caixas de seleção, nunca botões), e os cabeçalhos de painel não têm ícones.
- **Ferramentas de gesto:** Posicionar marcadores do rig (clique na malha para posicionar o próximo marcador do Assistente de Auto-Rig) e Construir mecanismo (clique numa peça para começar uma articulação ou ligação) estão na barra de ferramentas da viewport.
- **Dicas de ferramenta:** cada operador e cada opção se explica.
- **Mostrar, não esconder:** as seções continuam visíveis e dizem o que selecionar quando o rig some, o Assistente de Auto-Rig vem primeiro no Rig Builder, e as barras laterais abrem largas o bastante para ler.
- **Correções:** Gerar Spline IK volta a funcionar; Adicionar influência usa o osso escolhido; as prévias de visemas usam o seu conjunto.

## 9.0.0 (outubro de 2026)

- **Mechanisms:** uma nova seção da aba BoneCraft (e da aba Cena de Propriedades) que faz o rig de acessórios e máquinas: Hinge, Slide, Telescope, Piston, Gear Link, Follow e Sequence, construídos com passos guiados e conferidos com Test. O BoneCraft nunca sobrescreve uma mudança feita à mão: você escolhe **Keep mine** para mantê-la ou **Restaurar** para reconstruir. Veja [Mechanisms (mecanismos)](07-mechanisms.md).
- **Lados das abas:** cada aba da viewport pode ficar na Tool Shelf da esquerda ou na barra lateral da direita (Preferências → Tabs → Left / Right). BoneCraft e Rig Builder começam à esquerda, CATS à direita.
- **Construtor de Rig:** sempre na aba Cena de Propriedades, além da sua própria aba na viewport com um layout compacto para uma Tool Shelf estreita. Um rig Basic Humanoid vem na biblioteca de assets BoneCraft Rigs; Fit Dropped Rig ajusta um rig solto da prateleira de assets.
- **Aba CATS:** Importar / Exportar foi para a aba CATS. CATS, VRChat e Importar / Exportar também ficam sempre na aba Cena.
- **Show Helpers:** uma única preferência mostra ou oculta o texto didático do BoneCraft; o Modo Compacto é o atalho dela.
- **Validador de Rig:** nomes de ossos com hífens passam; os drivers só avisam em expressões que precisam de Python; os rigs de Mechanisms também são verificados. A tarefa do validador no Quadro de Tarefas volta a informar.
- **Nome:** o add-on se chama BoneCraft.

## 8.9.x (setembro–outubro de 2026)

- **8.9.6:** a peça inteira do vestido segue os ossos de saia (o quadril não atravessa mais); corretivos dos cantos da boca com a mandíbula aberta, com lábios pegajosos.
- **8.9.5:** troca IK/FK do cotovelo sem saltos; detecção simétrica dos ombros; os marcadores dos olhos não grudam mais sozinhos; o Control Picker mostra a seleção; cantos da boca mais redondos; uma correção do vestido sobre a coxa; clavículas de redirecionamento mais flexíveis; exportação em pose T.
- **8.9.4:** joelhos mais redondos (os corretivos substituem o Preserve Volume); chaves de contato para dobras profundas; uma mistura na junção do ombro.
- **8.9.3:** ossos de saia de dois segmentos que seguem as pernas e são empurrados por elas.
- **8.9.2:** piscada com shape keys (sem dobras nas pálpebras); uma abertura de boca oval.
- **8.9.1:** skinning muito mais rápido em malhas densas (678.000 vértices: de 232 s para 57 s); o calor dos ossos passa por uma malha proxy mais leve em vez de falhar em silêncio.
- **8.9.0:** shape keys corretivos de articulação; controles faciais (mira dos olhos, piscada, acompanhamento dos lábios); roupas que dobram com as articulações.
- Também na 8.9: recálculo automático de pesos de ossos e uma seleção de atlas mais clara.

## 8.7–8.8 (setembro de 2026)

- **8.8.0:** o painel de redirecionamento funciona em hosts Blender 5; marcadores dos dedos posicionados a partir da forma da mão; alongamento IK até a pele; uma opção Preserve Volume; uma correção do vínculo do Delta Mush.
- **8.7.0:** um rig de controle integrado; detecção de articulações percorrendo os membros; redirecionamento com direções correspondentes; ossos de torção.

## 8.5–8.6 (julho de 2026)

- **8.6.1–8.6.3:** Atlas de Materiais: diagnóstico dos blocos depois do bake; transparência MToon comparada com o alfa real da textura e mantida na criação do atlas; melhor divisão de materiais mistos.
- **8.5.5–8.5.10:** materiais VRM / MToon: o modo alfa é respeitado, o alfa funciona em hosts Blender 5, a emissão não estoura, diagnóstico em magenta e nomes de atlas seguros.
- **8.5.4:** o mapeamento humanoide é lido corretamente de novo; orientação para o Naming Prep.
- **8.5.2–8.5.3:** importação de um download do VRoid (.zip); um cartão de transição para projetos do VRoid.
- **8.5.1:** exportação FBX que mantém os blend shapes.

## Versões anteriores

**8.5.0:** o Smart Combine agora transforma `atlas_uv` no UV0 de exportação por padrão depois do bake. O mapa UV de origem anterior ao atlas é removido da malha de atlas gerada, a menos que **Keep Source UV Maps** (manter mapas UV de origem) esteja ativado nas configurações avançadas. Os controles do CATS / Material Combiner / derivados do UVToolkit agora são compartilhados com a versão aberta do Blender; a exclusividade do B4Artists continua nos sistemas de rigging de produção, controle, redirecionamento/exportação e publicação exclusivos do B4Artists.

A 8.5.0 também atualiza o fluxo de exportação e validação. As exportações de VRChat, VRM, MMD e Unreal agora mostram controles de pasta e nome de arquivo nos painéis do BoneCraft, em vez de obrigar você a depender só dos padrões do navegador de arquivos do Blender. As exportações FBX de VRChat/Unity e Unreal usam **Embed Textures** por padrão para facilitar a importação de materiais, enquanto a exportação do VRChat deixa de fora do FBX as malhas auxiliares e de formas de controle, a menos que **Helper Meshes** esteja ativado. O painel VRM agora inclui **Verificar Agora** e **Fix Humanoid Map**, que pode reparar antes da exportação um mapeamento de aliases humanoides desatualizado sem renomear seus ossos.

**8.4.5:** o Smart Combine agora força as texturas de origem a amostrar durante o bake o UV anterior ao atlas que foi preservado, valida a malha de atlas gerada antes de ocultar os originais e reatribui todas as faces do atlas ao slot de material final do atlas, para evitar pedaços de túnica ou roupa cinzas ou embaralhados.

**8.4.4:** o Combinador de atlas de materiais adiciona controles de inspeção de qualidade antes do bake: diagnóstico de shaders/materiais, rótulos de função das texturas, marcadores de origens duplicadas/compartilhadas, tamanhos forçados por material, presets de empacotamento, bakes opcionais de saídas Normal/Emission/Roughness e bloqueios prévios do empacotamento de canais Metallic/ORM até que esse caminho seja verificado.

**8.4.3:** o Combinador de atlas de materiais inclui métodos de empacotamento UV selecionáveis dentro do fluxo existente de Atlas de Materiais. Ele inclui Smart Pack, Grid Pack, Seeded Variation, Oriented Pack, Fit 0-1 Bounds, Advanced Variation e Rotation Step, com os detalhes do método UV registrados no relatório de depuração e no registro de bake.

**8.4.2:** o Combinador de atlas de materiais agora mira o UV do atlas gerado durante o bake, enquanto os nós de textura de origem copiados leem explicitamente o UV anterior ao atlas. Isso corrige resultados de atlas quebrados de túnicas/roupas, causados por texturas de origem e um atlas com bake que amostravam mapas UV diferentes. As linhas de materiais e texturas selecionáveis da 8.4.1 continuam disponíveis.

**7.1.3 (limpeza de rótulos de preferências):** dois interruptores das preferências do add-on foram renomeados para corresponder à aba da barra lateral que controlam. "VRChat Avatar Tools" agora se chama **CATS** (como a aba CATS). "Task Board & Sidebar" agora se chama **Rig Builder** (como a aba Rig Builder). Nenhuma ferramenta foi removida: só mudaram os rótulos de ligar/desligar em Editar > Preferências > Add-ons > BoneCraft.

**7.1.1:** o BoneCraft agora inclui as ferramentas do CATS: um conjunto completo de ferramentas de preparação de modelos feito para deixar os avatares do VRChat limpos, otimizados e totalmente configurados. O CATS tem sua própria aba na barra lateral e usa um sistema de pipeline que guia você, toda vez, pela ordem certa das operações.

Próximo: [Tutorial: Crescent Rose com Mechanisms](12-crescent-rose.md)
