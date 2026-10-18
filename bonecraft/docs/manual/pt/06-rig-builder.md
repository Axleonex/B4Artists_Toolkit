# Construtor de Rig

[← Sumário](index.md)

Para uma demonstração narrada dos dois tipos de rig, veja o [guia IK/FK para iniciantes e arquivo de prática](https://github.com/Axleonex/B4Artists_Toolkit/blob/main/bonecraft/docs/tutorials/ikfk-beginner.md).

## Construir um rig novo

O Construtor de Rig cria um rig novo para um personagem. Ele fica na sua própria aba **Rig Builder** da Tool Shelf da esquerda (pressione **T**), e  na aba **Cena** do editor de **Propriedades**. Em uma Tool Shelf estreita, ele muda para um layout compacto com rótulos curtos. Os painéis Cena aparecem quando Preferences → Tabs → Scene Properties → Show está ativado. Ocultar uma aba da viewport não oculta essa cópia.

---

Auto-Rig Wizard aparece primeiro, seguido de Quick Rig e Mannequin. Também pode iniciar o assistente ou adicionar um Quick Rig pelo menu Add → Armature da viewport.

### Assistente Auto-Rig

**O que faz:** um guia passo a passo que posiciona marcadores na sua malha e constrói a partir deles um rig com pesos. É o jeito principal de fazer o rig de um personagem do zero.

O [guia 1](02-guides-a.md#guia-1-leve-seu-primeiro-avatar-para-o-vrchat) percorre o assistente passo a passo.

**Passos:** Selecionar malha → Tipo de rig → Marcadores do corpo → Marcadores dos dedos → Marcadores do rosto → Revisão → Gerar

**Controles principais:**
- **Start Auto-Rig** abre o assistente. **Back** e **Cancel** ficam no topo; **Next** na base das etapas de malha, tipo e marcadores. Review usa **Generate Rig** no lugar de Next; a etapa final usa **Close Wizard**.
- A lista de malhas (clique na sua malha) e depois o tipo de rig: **Body + Face** (corpo e rosto), **Body Only** (só corpo) ou **Face Only** (só rosto, para uma armadura existente)
- **Detect Markers** (detectar marcadores; em Smart Detection) — percorre os membros da malha e posiciona cada marcador do corpo com um grau de confiança; **Accept High** (aceitar confiança alta) mantém os seguros e **Reset Low** (redefinir confiança baixa) apaga os duvidosos
- **Adivinhar marcadores da malha** e **Adivinhar precisão** (corpo), **Adivinhar marcadores de dedos** (os marcadores dos dedos são posicionados a partir da forma da mão) e **Adivinhar marcadores faciais**
- Detalhe dos Dedos — quantos dedos construir, de "0 — No Fingers" a "5 — Full Human Hand"
- A linha de cada marcador: **Place Marker** (posicionar marcador; ícone de seta), **Confirm Marker** (confirmar marcador; marca de verificação) e **Reset Marker** (redefinir marcador; seta circular); **Toggle Symmetry** (alternar simetria; primeiro ícone) nos marcadores esquerdos e direitos
- **Mirror L to R** (espelhar da esquerda para a direita) e **Mirror R to L** (espelhar da direita para a esquerda) — copiam os marcadores confirmados através da linha central
- **Confirmar todos colocados** — confirma cada marcador posicionado do passo
- **Gerar rig** — constrói o rig a partir dos marcadores confirmados; depois, no último passo, **Construir Rig de Controle** (veja abaixo) e **Fechar assistente**

**O que Gerar rig constrói:**
- Um rig de corpo com os segmentos de coluna e pescoço escolhidos, e braços e pernas IK/FK, só IK ou só FK (a opção **Cinemática**)
- Os ossos dos dedos para o número escolhido
- Para **Body + Face**: um rig facial, com formas de controle quando **Gerar formas de controle** está ativado
- Pesos de pele na qualidade escolhida. Malhas densas recebem pesos por meio de uma malha proxy mais leve, então um personagem de 678.000 vértices leva cerca de um minuto em vez de falhar em silêncio.

**Construir Rig de Controle:** o passo de revisão também mostra **Twist Bones** (ossos de torção), **Skirt Bones** (ossos de saia), **Face Controls** (controles faciais) e **Joint Correctives** (corretivos de articulação). Gerar rig não os aplica. Eles pertencem ao rig de controle para engines (ossos de torção, ossos de saia que seguem as pernas, controles de mira dos olhos e de piscada, e shape keys corretivos de articulação). Depois de Gerar rig, o último passo oferece **Construir Rig de Controle**, que constrói esse rig na armadura gerada com as opções escolhidas. Clique nele antes de **Fechar assistente**, porque fechar o assistente redefine as opções dele. O painel Control Layer (Ferramentas de rig) só aparece em um rig construído assim.

**Onde fica:** Rig Builder → Assistente Auto-Rig

---

**Vários marcadores pela viewport:** inicie o assistente e avance aos marcadores corporais, dos dedos ou rosto. Em Object Mode, ative Place Rig Markers na barra de ferramentas. O cabeçalho mostra o próximo marcador não confirmado, travas de eixo e simetria. Clique na malha do assistente para posicionar e confirmar. A simetria segue o assistente; os botões Place individuais continuam disponíveis. Quando indicar conclusão, clique em **Next**. Clicar fora da malha não coloca um marcador.

---

### Quick Rig (rig rápido)

**O que faz:** adiciona uma armadura pronta com um clique: Basic Humanoid de BoneCraft (19 ossos, sem Rigify) ou um metarig Rigify. Mais rápido que o assistente, menos personalizado.

**Controles principais:**
- Basic Humanoid e metarigs Rigify (**Enable Rigify** primeiro se estiver desligado).
- Clique para adicionar imediatamente; ajuste adaptação à malha, pesos automáticos, **Add IK/FK Controllers** e **Initial Pose** em Adjust Last Operation.
- **T-Pose** e **A-Pose** alteram a pose de repouso selecionada.
- Troubleshooting contém **Diagnose Quick Rig (print to console)**; com uma armadura que não é metarig também mostra **Inspect Active Rig Controls**.
- Com metarig Rigify ativo, **Generate Control Rig (active metarig)** substitui Inspect Active Rig Controls e gera o rig de controle Rigify.

**Catálogo inicial BoneCraft Rigs:** os nove rigs fornecidos compartilham o catálogo **Starter Rigs** na prateleira nativa de assets inferior. Abra o menu de catálogos à esquerda, escolha bibliotecas **All** e ative **Starter Rigs** uma vez para adicionar sua aba. Selecione-a para navegar. **Add → Armature → Starter Rig Catalog** abre o seletor com tratamento de dependências para adaptar e adicionar rigs.

Basic Humanoid dispensa Rigify. As outras miniaturas têm a marca **Rigify**. Se estiver inativo, selecionar ou soltar uma delas oferece **Enable Rigify & Add Rig** e Cancel. Aceitar ativa o Rigify instalado e continua com o preset; cancelar não adiciona nada. Também pode ativar Rigify em Quick Rig; o menu de contexto do asset no seletor oferece Enable Rigify quando necessário. Os controles iniciais no canto superior esquerdo da viewport foram removidos em 9.2.5. Dependência ausente ou preset indisponível na versão instalada gera uma explicação sem rig substituto.

Clique numa miniatura ou arraste para a viewport. Com malha selecionada, o rig se adapta a ela; pesos automáticos e geração de controles começam desligados. Ajuste em **Adjust Last Operation**. Sem malha selecionada, selecione o novo rig, escolha **Mesh** em Quick Rig e clique em **Fit Dropped Rig**. A adaptação escala e posiciona o esqueleto: inspecione e edite as articulações antes de gerar controles ou pesos. Soltar fora da viewport, Esc ou botão direito cancela sem adicionar nada.

**Onde encontrar:** Rig Builder → Quick Rig; Add → Armature → Quick Rig também adiciona os rigs prontos.

---

### Manequim

**O que faz:** cria uma malha de prévia em torno de um rig existente para avaliar deformações sem o personagem final. Selecione primeiro a armadura ou uma malha com ela como pai. Sem rig, adicione com Quick Rig. Substitua a prévia pela sua malha antes do uso final.

**Controles principais:**
- **Quick Mannequin** usa valores fixos e substitui o manequim anterior deste rig.
- **Add Mannequin** usa as configurações da cena e substitui o existente por padrão. Replace Existing fica em Adjust Last Operation após o clique.
- **Regenerate** reconstrói a prévia com suas configurações salvas.
- **Remove** apaga a malha e preserva a armadura.
- Options abaixo dos botões contém **Mode**, **Body Type**, densidade e **Radius Scale**; Advanced contém escalas regionais e saída. Para usar alterações na cena, clique novamente em **Add Mannequin**.

**Onde encontrar:** Rig Builder → Mannequin

---

## Oficina ilustrada do manequim

<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--oficina-ilustrada-do-manequim"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--parte-"] { break-before: page; break-after: avoid; }
  h3[id^="06-rig-builder--parte-"] + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Siga por ordem [A — Simple Human para manequim](#parte-a-simple-human-para-manequim), [B — manequim sem rig com Auto-Rig](#parte-b-manequim-sem-rig-com-auto-rig) e [C — testar pesos e usar IK/FK](#parte-c-testar-pesos-e-usar-ikfk). Cada passo numerado tem uma captura real; os números vermelhos correspondem à legenda. Capturas feitas com **BoneCraft 9.1.2** em `Bforartists 5.2.0`. Os painéis e atalhos do Blender podem diferir; use os nomes dos comandos como referência.

O exercício cria uma prévia em cápsulas para aprender rigging. Cabeça, mãos e tronco são provisórios, não um personagem finalizado. Comece num arquivo novo e preserve os dois pontos de salvamento para repetir a conversão sem perder o metarig original.

Ambos estão em `examples/mannequin/`: `SimpleHuman_Mannequin.blend` é o resultado neutro de A; `Mannequin_AutoRig.blend` é o exemplo concluído e posado de C, com pesos corrigidos.

### Parte A: Simple Human para manequim



#### A1. Ativar Rigify

Numa cena nova, abra **Scene Properties → Rig Builder → Quick Rig**. Se os presets Rigify estiverem indisponíveis, clique em **Enable Rigify**. Usamos o metarig Rigify `Simple Human`; **BoneCraft Basic Humanoid (19 bones)** é outro preset.

![A1. Ativar Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Scene Properties. 2 — Enable Rigify.*

#### A2. Adicionar Simple Human

Clique em `Simple Human` em Quick Rig. O resultado é um metarig editável, ainda sem malha. Nesta versão, ele tem 29 ossos.

![A2. Adicionar Simple Human](../images/rig-builder/en/a02-simple-human.png)

*1 — Preset Simple Human.*

#### A3. Inspecionar o metarig

Com o ponteiro na viewport, pressione `Numpad 1` para a vista ortográfica frontal. Confira se todo o esqueleto está visível; ajuste o enquadramento com a roda do mouse. O novo metarig pode começar em Pose Mode.

![A3. Inspecionar o metarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vista frontal. 2 — Esqueleto Simple Human.*

#### A4. Voltar ao Object Mode

No menu de modos da viewport, escolha **Object Mode**. Mantenha `SimpleHumanArmature` selecionado. Faça isso antes de mudar a pose de repouso ou gerar o manequim.

![A4. Voltar ao Object Mode](../images/rig-builder/en/a04-object-mode.png)

*1 — Menu de modos. 2 — Object Mode.*

#### A5. Usar uma T-pose

Em Quick Rig, clique em **T-Pose**: os braços ficam horizontais. Para um corpo personalizado, ajuste o metarig em Edit Mode antes de gerar a prévia; mantenha as articulações simétricas neste exercício.

![A5. Usar uma T-pose](../images/rig-builder/en/a05-t-pose.png)

*1 — Comando T-Pose.*

#### A6. Gerar o manequim

Expanda **Mannequin → Options**. Use `Mode: Universal`, `Body Type: Neutral`, **Medium** e `Radius Scale: 1.00`. Em Advanced, mantenha escalas regionais em 1.00, escolha `Joined (non-manifold)`, **Flat colour** e **Joint Smoothing**. Deixe Unified Volume desligado. Depois clique em **Add Mannequin**. A captura mostra a malha de cápsulas resultante. Add usa as opções atuais; Regenerate reutiliza as configurações salvas.

![A6. Gerar o manequim](../images/rig-builder/en/a06-final-settings.png)

*1 — Add Mannequin. 2 — Universal e configurações do corpo. 3 — Saída Joined e suavização.*

#### A7. Experimentar uma pose de osso

Selecione a armadura, entre em **Pose Mode** e clique no antebraço esquerdo do personagem (à sua direita na vista frontal). Gire-o um pouco com Rotate; o manequim acompanha. Esta prévia tem pesos no metarig, mas ainda não os controles de animação da parte C.

![A7. Experimentar uma pose de osso](../images/rig-builder/en/a07-select-forearm.png)

*1 — Pose Mode. 2 — Antebraço selecionado e gizmo de transformação.*

#### A8. Restaurar e salvar a prévia

Com o ponteiro na viewport, selecione todos os ossos de pose. Pressione **F3**, busque `Clear Pose Transforms` e escolha **All**. Confira o retorno à T-pose. Use **File → Save As** com o nome `SimpleHuman_Mannequin.blend`. Preserve esse ponto de salvamento.

![A8. Restaurar e salvar a prévia](../images/rig-builder/en/a09-clear-pose.png)

*1 — Busca Clear Pose Transforms. 2 — All redefine os ossos de pose selecionados.*

### Parte B: manequim sem rig com Auto-Rig



#### B1. Selecionar a malha do manequim

Continue do arquivo neutro de A. Em **Object Mode**, selecione `SimpleHumanArmature_Mannequin` no Outliner. Removeremos seu rig antes de usar o assistente. Salve com outro nome para preservar A.

![B1. Selecionar a malha do manequim](../images/rig-builder/en/b01-select-mesh.png)

*1 — Selecione a malha, não a armadura.*

#### B2. Converter a prévia em malha

Com apenas o manequim selecionado, pressione **F3**, procure `Convert Mesh` e execute. Isso preserva a geometria neutra visível e remove o modificador Armature. Faça com a T-pose restaurada.

![B2. Converter a prévia em malha](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Comando Convert Mesh.*

#### B3. Remover o parentesco

Pressione **Alt+P** e escolha `Clear and Keep Transformation`. Isso separa a malha do metarig antigo sem movê-la.

![B3. Remover o parentesco](../images/rig-builder/en/b03-clear-parent.png)

*1 — Clear and Keep Transformation.*

#### B4. Remover os pesos antigos

Abra **Object Data Properties → Vertex Groups**. No menu da lista, escolha `Delete All Groups`. Esses grupos pertencem ao metarig antigo; o assistente criará novos. Esta ação se destina à malha descartável de treinamento.

![B4. Remover os pesos antigos](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menu Vertex Groups. 2 — Delete All Groups.*

#### B5. Verificar a prévia sem rig

Oculte `SimpleHumanArmature` pelo olho no Outliner. O manequim deve continuar visível, sem modificador Armature e sem Vertex Groups. Esta é a entrada sem rig. BoneCraft 9.1.2 gera manequins a partir de armaduras; separar essa prévia produz a malha de treinamento sem rig.

![B5. Verificar a prévia sem rig](../images/rig-builder/en/b05-rigless-check.png)

*1 — Oculte o metarig antigo. 2 — Pilha de modificadores vazia.*

#### B6. Ativar a aba Rig Builder na viewport

Abra **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Ative **Rig Builder**, escolha **Left** e feche Preferences. Com o ponteiro na viewport, pressione **T** se a Tool Shelf esquerda estiver oculta. Use essa aba para os marcadores: no host 9.1.2 testado, Place Marker iniciado em Scene Properties não aceitava cliques na viewport.

![B6. Ativar a aba Rig Builder na viewport](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Ative Rig Builder. 2 — Posição na Tool Shelf esquerda.*

#### B7. Iniciar Auto-Rig

Com o manequim sem rig selecionado, clique em **Start Auto-Rig**. A captura mostra o botão equivalente em Scene Properties; o mesmo comando fica no topo da aba Rig Builder ativada antes.

![B7. Iniciar Auto-Rig](../images/rig-builder/en/b06-start-wizard.png)

*1 — Start Auto-Rig.*

#### B8. Escolher a malha de entrada

Em `Select Mesh`, escolha o manequim, verifique a confirmação de seleção e clique em **Next**. Não escolha um widget ou outra prévia.

![B8. Escolher a malha de entrada](../images/rig-builder/en/b07-select-input.png)

*1 — Manequim de entrada. 2 — Next.*

#### B9. Escolher um rig corporal com ambos os métodos

Escolha **Body Only** e `Kinematics: IK + FK`. Mantenha **Generate Control Shapes** ativado e clique em **Next**. Este manequim de cápsulas não tem topologia facial, portanto dispensa Body + Face.

![B9. Escolher um rig corporal com ambos os métodos](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Body Only. 2 — IK + FK. 3 — Next.*

#### B10. Detectar os primeiros marcadores corporais

Em Body Markers, clique em **Detect Markers** sob Smart Detection. As estimativas são um ponto de partida. Mantenha **Mirror Symmetry** para este manequim simétrico; confira cada estimativa antes de aceitá-la.

![B10. Detectar os primeiros marcadores corporais](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detect Markers. 2 — Mirror Symmetry.*

#### B11. Revisar as posições detectadas

Confira topo da cabeça, base do pescoço, pelve, punhos e tornozelos contra a malha. Esta prévia segmentada gera várias estimativas de baixa confiança. Corrija os marcos principais e os opcionais de precisão antes de gerar. Os índices de confiança descrevem a detecção original; a marca verde no início da linha confirma o posicionamento atual.

![B11. Revisar as posições detectadas](../images/rig-builder/en/b10-review-markers.png)

*1 — Resumo da confiança de detecção. 2 — Linhas dos marcadores corporais.*

#### B12. Colocar um punho na malha

Na aba **Rig Builder** da viewport, clique no conta-gotas **Place Marker** de Wrist Left e depois na superfície do punho. Se o marcador estiver confirmado, redefina a linha primeiro para exibir o botão. Na vista frontal, o punho esquerdo do personagem fica à direita da tela.

![B12. Colocar um punho na malha](../images/rig-builder/en/b11-place-wrist.png)

*1 — Controle de posicionamento Wrist Left. 2 — Clique na superfície do punho.*

#### B13. Conferir o punho espelhado e tornozelos

Os dois punhos devem mostrar marcas verdes e coordenadas X opostas. Repita para `Ankle Left`; a simetria fornece Ankle Right. Coloque cada tornozelo na articulação, não nos dedos do pé. Confira na malha; não copie coordenadas do exemplo para personagens de outro tamanho.

![B13. Conferir o punho espelhado e tornozelos](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — Par de punhos confirmado. 2 — Punho espelhado na malha.*

#### B14. Refinar ombros e cotovelos

Em Precision Markers, redefina e coloque `Shoulder Left` no pivô do braço e `Elbow Left` no espaço do cotovelo. Confirme seus pares espelhados. O punho fica na extremidade do antebraço junto à mão. Esses pontos definem a cadeia do braço; corrija ombros ou cotovelos estimados na cápsula errada.

![B14. Refinar ombros e cotovelos](../images/rig-builder/en/b13-arm-precision.png)

*1 — Linhas do ombro e cotovelo. 2 — Ombro. 3 — Cotovelo.*

#### B15. Refinar quadris e joelhos

Coloque `Hip Left` no topo da coxa e `Knee Left` no espaço entre coxa e canela. Confira o lado espelhado. Mantenha a pelve no centro, entre os quadris.

![B15. Refinar quadris e joelhos](../images/rig-builder/en/b14-leg-precision.png)

*1 — Linhas do quadril e joelho. 2 — Superfície do quadril. 3 — Espaço do joelho.*

#### B16. Conferir profundidade e dedos de lado

Com o ponteiro na viewport, pressione `Numpad 3`. Confira os marcos na vista ortográfica direita e frontal. Coloque `Toe Left` perto da frente do pé e confira seu par. Um marcador correto de frente pode estar adiantado ou recuado no perfil.

![B16. Conferir profundidade e dedos de lado](../images/rig-builder/en/b15-side-depth.png)

*1 — Vista ortográfica direita. 2 — Linha do dedo do pé. 3 — Superfície do pé.*

#### B17. Colocar os calcanhares

Redefina o calcanhar estimado incorretamente e coloque `Heel Left` perto da traseira do pé na vista lateral. Confira Heel Right. Embora opcionais, deixar ambos em zero causou um aviso de proximidade na versão testada; posicioná-los nos pés eliminou o aviso.

![B17. Colocar os calcanhares](../images/rig-builder/en/b16-place-heels.png)

*1 — Par de calcanhares confirmado. 2 — Local do calcanhar.*

#### B18. Confirmar e continuar

Revise topo da cabeça, base do pescoço, pelve e todos os marcos pareados. Clique em **Confirm All Placed**, depois **Next**. As marcas verdes indicam confirmação; os índices originais REVIEW/ADJUST podem continuar visíveis em 9.1.2.

![B18. Confirmar e continuar](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirm All Placed. 2 — Next.*

#### B19. Ignorar dedos nesta malha

Escolha `0 — No Fingers`, depois **Next**. As mãos são cápsulas sem geometria de dedos. Numa mão real, escolha a contagem adequada e posicione seus marcadores.

![B19. Ignorar dedos nesta malha](../images/rig-builder/en/b18-no-fingers.png)

*1 — No Fingers. 2 — Next.*

#### B20. Revisar e gerar

Exija **All checks passed**. Use **IK + FK**, formas de controle ativadas, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` e **Game Ready**. Desative Twist Bones, Skirt Bones, Preserve Volume e Joint Correctives. Clique em **Generate Rig**. São configurações para este manequim simples, não uma receita universal de exportação.

![B20. Revisar e gerar](../images/rig-builder/en/b19-review-generate.png)

*1 — Verificações dos marcadores. 2 — Configurações de geração. 3 — Generate Rig.*

#### B21. Construir os controles de animação

Após gerar, clique em **Build Control Rig**. Generate Rig fornece o corpo e os pesos; Build Control Rig adiciona a camada de controles usada abaixo. Não clique em Quick Mannequin novamente: a malha já existe, mesmo se o painel final oferecer genericamente um manequim.

![B21. Construir os controles de animação](../images/rig-builder/en/b20-build-controls.png)

*1 — Build Control Rig.*

#### B22. Concluir o assistente

Aguarde a mensagem de conclusão do rig de controle e clique em **Close Wizard**. A nova armadura aparece no Outliner. Mantenha o metarig Simple Human antigo oculto. O rig precisa deformar a malha; apenas ver ossos não valida o resultado.

![B22. Concluir o assistente](../images/rig-builder/en/b21-close-wizard.png)

*1 — Botão de construção agora desativado. 2 — Close Wizard.*

### Parte C: testar pesos e usar IK/FK

Na versão testada, a armadura gerada recebe este nome de objeto (use no Outliner e na ferramenta de pesos):

```text
BoneForge_Rig
```

`FK (Forward Kinematics)`, cinemática direta: rotações seguem a hierarquia, braço, antebraço e mão. Serve para movimentos amplos e membros livres. `IK (Inverse Kinematics)`, cinemática inversa: mova a meta do punho ou tornozelo; o solver dobra a cadeia para alcançá-la. Serve para pés plantados e mãos apoiadas em superfícies.

| Tarefa | Controle | O que observar |
|---|---|---|
| Balançar um braço | Ombro e cotovelo FK | Os filhos seguem o pai |
| Posicionar uma mão | Meta IK do punho | Ombro e cotovelo buscam a meta |
| Plantar um pé | Meta IK do tornozelo dessa perna | Mova o corpo mantendo a meta alcançável no lugar |
| Orientar cotovelo ou joelho | Polo IK | Define a direção da dobra; não é a meta de punho/tornozelo |
| Trocar método | Botões IK/FK do membro | Confira o alinhamento da pose antes de inserir chaves |

O exercício compara um braço nos dois modos. Cada membro tem sua chave. `Bake IK / Bake FK` converte animações; trocar uma pose não substitui bake ou criação de chaves. Veja [Camada de controle](05-rig-tools.md#control-layer-camada-de-controle-ikfk).

#### C1. Abrir a camada de controle

Selecione a **armadura gerada**, entre em **Pose Mode** e abra **BoneCraft → Review → Control Layer**. Cada braço e perna tem sua chave IK/FK. Comece em **arm-L → FK**. Esquerda e direita são do personagem: arm-L fica à sua direita na vista frontal.

![C1. Abrir a camada de controle](../images/rig-builder/en/c02-control-layer.png)

*1 — Pose Mode. 2 — Control Layer e chave arm-L.*

#### C2. Mostrar os controles de animação

Abra **Object Data Properties → Bone Collections** da armadura. Use as estrelas Solo de `Controls` e **FK** para isolar suas formas. Ative **In Front** em Viewport Display se a malha ocultar os controles. Depois inclua **IK** para as metas. Essa lista nativa também funciona se o painel Collections de BoneCraft não desenhar neste host.

![C2. Mostrar os controles de animação](../images/rig-builder/en/c03-visible-controls.png)

*1 — Estrelas Solo de Controls e FK. 2 — In Front.*

#### C3. Selecionar o controle FK do antebraço

Na vista frontal, clique no círculo no cotovelo esquerdo do personagem. Verifique o nome **forearm.fk-L**. Esse controle gira no cotovelo; selecionar o ombro giraria o braço e seus filhos.

![C3. Selecionar o controle FK do antebraço](../images/rig-builder/en/c04-select-fk.png)

*1 — Controle forearm.fk-L selecionado. 2 — FK ativo em arm-L.*

#### C4. Girar e inspecionar a deformação

Gire o controle FK cerca de `−45°` em **Y** global neste exemplo frontal. Use Rotate; no mapa de teclas Bforartists mostrado: **Ctrl+E**, **Y**, **-45**, **Enter**. No Blender padrão é **R**. A captura mostra intencionalmente o problema inicial de pesos: a cápsula do braço inclina com o antebraço. Não aceite como rig final.

![C4. Girar e inspecionar a deformação](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — Movimento incorreto do braço no teste FK.*

#### C5. Recalcular os pesos do manequim

Se o teste falhar, entre em **Object Mode**, selecione a malha e abra **BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. Mesh to Reweight: manequim; Existing Armature: **armadura gerada**. Escolha **Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0`, `Minimum Weight: 0.001`. Mantenha **Keep Weight Backup** ativado e execute **Automatic Bone Weight Recalculation**. Isso reparou a prévia segmentada na versão testada.

![C5. Recalcular os pesos do manequim](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Malha e armadura. 2 — Bone Heat. 3 — Substituição e backup. 4 — Recalcular.*

#### C6. Conferir a dobra FK corrigida

Selecione a armadura gerada e volte ao **Pose Mode**. O braço deve permanecer horizontal do ombro ao cotovelo, enquanto o antebraço sobe a partir do cotovelo. O objeto oculto `WEIGHTS_BACKUP_…` preserva os pesos antigos. Teste os outros membros antes de animar seu personagem; gerar um esqueleto não comprova pesos corretos.

![C6. Conferir a dobra FK corrigida](../images/rig-builder/en/c05-fk-result.png)

*1 — Braço permanece no lugar. 2 — Antebraço dobra no cotovelo.*

#### C7. Trocar o mesmo braço para IK

Clique em **arm-L → IK**. A meta se alinha à pose atual; o braço deve permanecer levantado. Inclua **IK** nas coleções Solo visíveis se necessário. Trocar muda os controles que dirigem a cadeia; não grava animação.

![C7. Trocar o mesmo braço para IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — Chave arm-L IK. 2 — Pose preservada na troca.*

#### C8. Selecionar a meta IK do punho

Clique no controle do punho e confira **forearm.ik-L**. Apesar do nome de antebraço, é a meta da extremidade da cadeia. Mova-a para posicionar a mão; o solver ajusta ombro e cotovelo.

![C8. Selecionar a meta IK do punho](../images/rig-builder/en/c07-select-ik.png)

*1 — Meta do punho selecionada. 2 — Nome da seleção.*

#### C9. Mover a meta e comparar

Mova a meta ligeiramente para dentro em **X** global. Aqui `−0.15 m` muda claramente a dobra. No mapa mostrado: **Ctrl+W**, **X**, `-0.15`, **Enter**, ou arraste a seta X de Move. No Blender padrão é **G**. Compare com FK: a extremidade conduz e ambos os segmentos acompanham. Mantenha a meta ao alcance do braço.

![C9. Mover a meta e comparar](../images/rig-builder/en/c08-move-ik.png)

*1 — Extremidade do punho. 2 — Resposta da cadeia. 3 — Movimento X do exemplo.*

#### C10. Voltar a FK e salvar

Clique novamente em **arm-L → FK**; os controles FK se alinham à pose IK. Confira se a malha não salta e use **File → Save As** para `Mannequin_AutoRig.blend`. A captura mostra o exemplo salvo com FK ativo. Para uma cópia neutra, deixe os quatro membros em FK, selecione todos os controles de pose visíveis e use **F3 → Clear Pose Transforms → All**, como em A; salve com outro nome.

![C10. Voltar a FK e salvar](../images/rig-builder/en/c10-save-complete.png)

*1 — FK ativo novamente. 2 — Pose preservada. 3 — Nome salvo.*

**Verificação final:** prévia do metarig original preservada, manequim separado sem rig, corpo e controles gerados, pesos corrigidos e comparação entre rotação FK e movimento de meta IK. Guarde como exemplo de estudo; substitua a prévia por geometria adequada para produção.

---

### Redirecionamento de animação

Passar uma animação de um esqueleto para outro é tratado em [Ferramentas de rig: Redirecionar](05-rig-tools.md#redirecionar).

---

## Mesclagem de Ossos

**O que faz:** combina duas armaduras em uma (por exemplo, um rig de corpo e um rig de roupa ou de cabelo), mantendo todos os pesos.

O [guia 11](03-guides-b.md#guia-11-junte-dois-rigs) percorre o processo passo a passo.

**As três etapas:**
1. Escopo — escolher as duas armaduras e revisar as diferenças
2. Renomear — resolver conflitos de nomes e marcar os ossos novos
3. Mesclar — pré-visualizar e depois mesclar

**Controles principais:**
- **Base** — a armadura que fica; a outra é mesclada nela e depois ocultada
- **Analyze** (analisar) — compara os dois esqueletos; **Acknowledge Scope — Proceed to Rename** (confirmar escopo — seguir para renomear) abre a etapa 2
- **Normalize Both Armatures** (normalizar as duas armaduras) — renomeia os ossos padrão dos dois rigs para um mesmo padrão de nomes (Mixamo Prefixed, Mixamo Stripped ou personalizado)
- **Auto-Propose Renames** (propor renomeações automaticamente) — sugere nomes para os ossos próprios do rig mesclado
- **Apply Rename** (aplicar renomeação) — renomeia uma entrada (um passo de desfazer); **Apply Batch Pattern** (aplicar padrão em lote) renomeia muitas com um padrão (com `{bone}`, `{side}` e `{index}`)
- **Mark as Unique** (marcar como único) — mantém um osso como osso novo em vez de mesclá-lo
- **Verify Rename — Proceed to Merge** (verificar renomeação — seguir para mesclar) — abre a etapa 3
- **Run Merge Preview** (executar pré-visualização da mesclagem) — informa o que a mesclagem faria, sem mudar nada
- **Mesclar Armaduras** — faz backup das duas armaduras e as mescla

**Onde fica:** BoneCraft → Setup Rigging → Bone Merge

Próximo: [Mechanisms (mecanismos)](07-mechanisms.md)
