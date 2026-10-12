# Construtor de Rig

[← Conteúdo](index.md)

## Construir um rig novo

O Rig Builder cria um novo rig para um personagem. Ele está em sua própria guia **Rig Builder** na prateleira de ferramentas esquerda (pressione**T**) e na guia**Properties** do editor**Scene** enquanto Preferências → Guias → Propriedades da cena → Mostrar está ativado. Em uma prateleira de ferramentas estreita, ele muda para um layout compacto com etiquetas curtas. O Auto-Rig Wizard vem primeiro, seguido pelo Quick Rig e Mannequin. Você também pode iniciar o assistente ou adicionar um Quick Rig no menu Adicionar → Armadura da viewport.

---

### Assistente Auto-Rig

**O que faz:** um guia passo a passo que coloca marcadores em sua malha e constrói um rig completo com pesos a partir deles. A principal forma de manipular um personagem do zero.

[Guia 1](02-guides-a.md#guia-1-leve-seu-primeiro-avatar-para-o-vrchat) percorre isso passo a passo.

**Etapas:** Selecione Malha → Tipo de rig → Marcadores corporais → Marcadores de dedos → Marcadores faciais → Revisão → Gerar

**Controles principais:**
- **Start Auto-Rig** abre o assistente.**Back** e**Cancel** estão no topo;**Next** está na parte inferior das etapas de malha, tipo de rig e marcador. A revisão usa**Generate Rig** em vez de Próximo; a etapa final usa**Close Wizard**
- A lista de malhas (clique na sua malha) e, em seguida, o tipo de rig: **Body + Face**,**Body Only** ou**Face Only** (para uma armadura existente)
- **Detect Markers** (em Smart Detection) — traça os membros na malha e coloca cada marcador corporal com confiança;**Accept High** mantém os seguros e**Reset Low** elimina os duvidosos
- **Guess Markers from Mesh** e**Guess Precision** (corpo),**Guess Finger Markers** (marcadores de dedo são colocados a partir do formato da mão) e**Guess Face Markers**
- Detalhe dos dedos — quantos dedos construir, de "0 — Sem dedos" a "5 — Mão humana completa"
- A linha de cada marcador: **Place Marker** (ícone de seta),**Confirm Marker** (marca de seleção) e**Reset Marker** (seta circular);**Toggle Symmetry** (primeiro ícone) nos marcadores esquerdo e direito
- **Mirror L to R** e**Mirror R to L** — copia marcadores confirmados através da linha central
- **Confirm All Placed** — confirma cada marcador colocado na etapa
- **Generate Rig** — constrói o rig a partir dos marcadores confirmados; então, na última etapa,**Build Control Rig** (veja abaixo) e**Close Wizard**

**O que o Generate Rig compila:**
- Um body rig com os segmentos de coluna e pescoço que você escolheu e braços e pernas IK/FK, apenas IK ou apenas FK (a opção **Kinematics** )
- Ossos dos dedos para a contagem de dedos que você escolheu
- Para **Body + Face**: um rig facial, com formatos de controle quando**Generate Control Shapes** está ativado
- Pesos de pele na qualidade escolhida. Malhas densas são ponderadas por meio de uma malha proxy mais leve, de modo que um caractere de 678.000 vértices leva cerca de um minuto em vez de falhar silenciosamente.

**Build Control Rig:** a etapa de revisão também mostra**Twist Bones**,**Skirt Bones**,**Face Controls** e**Joint Correctives**. Generate Rig não os aplica. Eles pertencem ao rig de controle do motor (ossos de torção, ossos da saia que seguem as pernas, mira ocular e controles de piscar e chaves de formato corretivo de articulações). Após Generate Rig, a última etapa oferece**Build Control Rig**, que constrói esse rig na armadura gerada com as opções que você escolheu. Clique nele antes de**Close Wizard**, pois fechar redefine as opções do assistente. O painel Control Layer (Rig Tools) aparece apenas em um rig construído desta forma.

**Onde encontrar:** Rig Builder → Auto-Rig Wizard

**Coloque vários marcadores com a ferramenta viewport:** inicie o assistente e avance para uma etapa de marcador de corpo, dedo ou rosto. No modo de objeto, ative Place Rig Markers na barra de ferramentas da viewport. O cabeçalho da ferramenta nomeia o próximo marcador não confirmado e mostra bloqueios de eixo e uma troca de espelho. Clique na malha do assistente para posicionar e confirmar esse marcador. A simetria segue as configurações do assistente; os botões Place por marcador ainda funcionam. Quando a ferramenta disser que a etapa foi concluída, pressione**Next** no assistente. Clicar em outro lugar não coloca um marcador.

---

### Quick Rig (rig rápido)

**O que ele faz:** Adiciona uma armadura pronta com um clique: Humanóide Básico de BoneCraft (19 ossos, não é necessário Rigify ) ou um dos metarigs de Rigify. Mais rápido que o assistente, menos personalizado.

**Controles principais:**
- O botão Basic Humanoid e os metarigs Rigify (**Enable Rigify** primeiro, se Rigify estiver desligado)
- Clique em um botão de rig para adicioná-lo imediatamente e, em seguida, ajuste o ajuste à malha, pesos automáticos, **Add IK/FK Controllers** e**Initial Pose** em Ajustar última operação
- **T-Pose** e**A-Pose** — alterna a pose de descanso do rig selecionado
- Expanda Solução de problemas para **Diagnose Quick Rig (print to console)**. Com uma armadura não metarig ativa, ele também mostra**Inspect Active Rig Controls**
- Com um metarig Rigify ativo, a solução de problemas mostra **Generate Control Rig (active metarig)** em vez de Inspecionar controles ativos do rig; ele gera o rig de controle Rigify

**A biblioteca de ativos BoneCraft Rigs:** o Humanóide Básico também é um ativo. Arraste-o da prateleira de recursos para o seu personagem. Com o rig descartado selecionado, Quick Rig mostra "rig descartado: ajuste-o a uma malha": escolha**Mesh** e clique em**Fit Dropped Rig**. Imediatamente depois, use**Fit Rig to Mesh** e**Parent + Auto-Weight Mesh** em Ajustar última operação para escolher o ajuste e a ponderação. Uma nova operação tem como padrão o ajuste ativado e a ponderação automática desativada.

**Onde encontrar:** Rig Builder → Quick Rig; Adicionar → Armadura → Quick Rig também adiciona os rigs pré-fabricados

---

### Manequim

**O que ele faz:** Cria uma malha de visualização em torno de um rig existente para que você possa inspecionar sua deformação sem uma malha de personagem finalizada. Selecione primeiro a armadura ou uma malha parente dela. Se você ainda não tem rig, adicione um com Quick Rig. O manequim é apenas uma prévia: substitua-o pela sua própria malha antes do uso final.

**Controles principais:**
- **Quick Mannequin** — cria uma visualização com padrões fixos, substituindo o modelo antigo para este rig
- **Add Mannequin** — cria uma visualização usando as configurações da cena; ele substitui um manequim existente por padrão. Substituir Existente está em Ajustar Última Operação após o clique
- **Regenerate** — reconstrói a visualização existente usando suas configurações salvas
- **Remove** — exclui a malha do manequim e mantém a armadura
- Expanda Opções abaixo dos botões para **Mode**,**Body Type**, densidade e**Radius Scale**; Avançado em Opções contém as escalas de região e configurações de saída. Para usar as configurações de cena alteradas, clique em**Add Mannequin** novamente

**Onde encontrar:** Rig Builder → Manequim

---

## Oficina de manequins ilustrados

<!-- Keep each illustrated step together and preserve the manual's print scale. -->
<style>
section.chapter:has(#ch-06-rig-builder) img { max-width: 100%; max-height: 155mm; width: auto; height: auto; }
@media print {
  [id="06-rig-builder--oficina-de-manequins-ilustrados"] { break-before: page; break-after: avoid; }
  h4[id^="06-rig-builder--"] { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--parte-a-humano-simples-para-manequim"],[id="06-rig-builder--parte-b-manequim-rigless-através-do-auto-rig"],[id="06-rig-builder--parte-c-teste-de-pesos-e-uso-ikfk"]) { break-before: page; break-after: avoid; }
  :is([id="06-rig-builder--parte-a-humano-simples-para-manequim"],[id="06-rig-builder--parte-b-manequim-rigless-através-do-auto-rig"],[id="06-rig-builder--parte-c-teste-de-pesos-e-uso-ikfk"]) + h4 { break-before: avoid; }
  section.chapter:has(#ch-06-rig-builder) h4 + p { break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) { break-before: avoid; break-after: avoid; }
  section.chapter:has(#ch-06-rig-builder) p:has(> img) + p { break-before: avoid; }
}
</style>

Siga estas três partes em ordem: [A - Humano Simples para Manequim](#parte-a-humano-simples-para-manequim), [B – manequim sem rigless através do Auto-Rig](#parte-b-manequim-rigless-através-do-auto-rig) e [C – pesos de teste e uso IK/FK](#parte-c-teste-de-pesos-e-uso-ikfk). Cada etapa numerada possui uma captura de tela real da interface; os números vermelhos correspondem à legenda. As capturas de tela foram capturadas com a versão **BoneCraft 9.1.2** em `Bforartists 5.2.0`. A disposição do painel e os atalhos do Blender podem ser diferentes; os comandos nomeados são a referência.

Este exercício produz uma visualização simples da cápsula para aprender rigging. Sua cabeça, mãos e torso são espaços reservados e não é um modelo de personagem acabado. Comece em um novo arquivo; mantenha os dois checkpoints salvos para poder repetir a conversão sem perder o metarig original.

O repositório inclui ambos os pontos de verificação em `examples/mannequin/`: `SimpleHuman_Mannequin.blend` é o resultado neutro da Parte A e `Mannequin_AutoRig.blend` é o exemplo da Parte C completo e colocado com pesos corrigidos.

### Parte A: Humano Simples para Manequim

#### A1. Ativar Rigify

Comece em uma nova cena. Abra **Scene Properties → Rig Builder → Quick Rig**. Se as predefinições Rigify não estiverem disponíveis, clique em**Enable Rigify**. Este tutorial usa o metarig Rigify `Simple Human`;**BoneCraft Basic Humanoid (19 bones)** é uma predefinição diferente.

![A1: Habilitar Rigify](../images/rig-builder/en/a01-enable-rigify.png)

*1 — Propriedades da Cena. 2 — Habilite Rigify.*

#### A2. Adicionar Humano Simples

Clique em `Simple Human` em Quick Rig. O resultado é uma metarig editável, ainda não uma malha. Possui 29 ossos nesta versão.

![A2: Adicionar Humano Simples](../images/rig-builder/en/a02-simple-human.png)

*1 — Predefinição Humana Simples.*

#### A3. Inspecione o metarig

Mova o ponteiro para a janela de visualização e pressione `Numpad 1` para Front Orthographic. Verifique se todo o esqueleto está visível. Use a roda do mouse para enquadrá-lo. O novo metarig pode começar no modo Pose.

![A3: Inspecione o metarig](../images/rig-builder/en/a03-metarig.png)

*1 — Vista frontal. 2 — Esqueleto humano simples.*

#### A4. Retornar ao modo de objeto

Use o menu suspenso do modo de janela de visualização e escolha **Object Mode**. Mantenha `SimpleHumanArmature` selecionado. Escolha o Modo de Objeto antes de alterar a pose de repouso ou gerar o manequim.

![A4: Retornar ao modo de objeto](../images/rig-builder/en/a04-object-mode.png)

*1 — Menu suspenso de modo. 2 — Modo Objeto.*

#### A5. Use uma pose em T

No Quick Rig, clique em **T-Pose**. Os braços se estendem horizontalmente. Para um corpo personalizado, ajuste o metarig no Edit Mode antes de gerar sua visualização; mantenha as articulações esquerda e direita simétricas para este exercício.

![A5: Use uma pose em T](../images/rig-builder/en/a05-t-pose.png)

*1 — Comando T-Pose.*

#### A6. Gere o manequim

Expanda **Mannequin → Options**. Defina `Mode: Universal`, `Body Type: Neutral`,**Medium** e `Radius Scale: 1.00`. Em Avançado, mantenha as escalas de região em 1,00, escolha `Joined (non-manifold)`,**Cor plana** e ative**Joint Smoothing**. Deixe o Volume Unificado desativado. Clique em**Add Mannequin** após definir essas opções. A captura de tela mostra a malha da cápsula resultante. Use Adicionar para opções atuais; Regenerar reutiliza as configurações salvas do manequim.

![A6: Gere o manequim](../images/rig-builder/en/a06-final-settings.png)

*1 — Adicionar Manequim. 2 — Configurações universais e corporais. 3 — Saída unida e suavização.*

#### A7. Experimente uma pose de osso

Selecione a armadura, mude para **Pose Mode** e clique no osso do antebraço esquerdo (a esquerda do personagem está à sua direita na vista frontal). Gire levemente com a ferramenta Girar; segue o manequim anexo. Esta é uma visualização ponderada no metarig. Ainda não possui os controles do animador usados na Parte C.

![A7: Experimente uma pose de osso](../images/rig-builder/en/a07-select-forearm.png)

*1 — Modo de pose. 2 — Antebraço selecionado e seu dispositivo de transformação.*

#### A8. Restaure e salve a visualização

Com o ponteiro na viewport, selecione todos os ossos de pose. Pressione **F3**, pesquise `Clear Pose Transforms` e escolha**Todos**. Confirme se o manequim retorna à pose em T. Use**File → Save As** e nomeie o arquivo como `SimpleHuman_Mannequin.blend`. Mantenha este ponto de verificação antes de continuar.

![A8: Restaure e salve a visualização](../images/rig-builder/en/a09-clear-pose.png)

*1 — Limpar pesquisa de Pose Transforms. 2 — Tudo redefine os ossos de pose selecionados.*

### Parte B: Manequim Rigless através do Auto-Rig

#### B1. Selecione a malha do manequim

Continue a partir do ponto de verificação neutro na Parte A. Mude para **Object Mode** e selecione `SimpleHumanArmature_Mannequin` no Outliner. Removeremos deliberadamente seu rig antes de executar o assistente. Salve o resultado com um nome de arquivo diferente para preservar a Parte A.

![B1: Selecione a malha do manequim](../images/rig-builder/en/b01-select-mesh.png)

*1 — Selecione a malha, não a armadura.*

#### B2. Transforme a visualização em uma malha

Com apenas o manequim selecionado, pressione **F3**, pesquise `Convert Mesh` e execute-o. Isso mantém a geometria neutra visível e remove o modificador Armadura. Faça isso com o manequim em sua pose em T restaurada.

![B2: Transforme a visualização em uma malha](../images/rig-builder/en/b02-convert-mesh.png)

*1 — Comando Converter Malha.*

#### B3. Limpe o pai

Pressione **Alt+P** e escolha `Clear and Keep Transformation`. Isso separa a malha do metarig antigo sem movê-la.

![B3: Limpe o pai](../images/rig-builder/en/b03-clear-parent.png)

*1 — Limpe e mantenha a transformação.*

#### B4. Remova os pesos antigos

Abra **Object Data Properties → Vertex Groups**. No menu suspenso da lista, escolha `Delete All Groups`. Esses grupos pertencem ao antigo metarig; o assistente criará novos. Esta ação é para esta malha de treino descartável.

![B4: Remova os pesos antigos](../images/rig-builder/en/b04-clear-groups.png)

*1 — Menu Grupos de vértices. 2 — Excluir todos os grupos.*

#### B5. Verifique o ponto de verificação sem rig

Oculte o antigo `SimpleHumanArmature` usando o ícone do olho Outliner. Verifique se o manequim permanece visível, se o painel Modificadores não possui modificador de armadura e se a lista de grupos de vértices está vazia. Esta é a entrada do modelo sem rigless. BoneCraft 9.1.2 gera manequins a partir de uma armadura; separar essa visualização é o caminho para uma malha de treinamento sem rigless.

![B5: Verifique o ponto de verificação sem plataforma](../images/rig-builder/en/b05-rigless-check.png)

*1 — Esconda o metarig antigo. 2 — Pilha modificadora vazia.*

#### B6. Habilite a guia Rig Builder da janela de visualização

Abra **Edit → Preferences → Add-ons → BoneCraft → Tabs**. Habilite**Rig Builder** e escolha**Left**. Feche Preferências, coloque o ponteiro sobre a janela de visualização e pressione**T** se a prateleira de ferramentas esquerda estiver oculta. Use esta guia da viewport para posicionamento do marcador: no host 9.1.2 testado, iniciar o Place Marker nas Propriedades da cena não aceitava cliques na viewport.

![B6: Habilite a guia Rig Builder da janela de visualização](../images/rig-builder/en/b10a-enable-rig-builder-tab.png)

*1 — Habilite o Construtor de Plataforma. 2 — Posicionamento da prateleira de ferramentas esquerda.*

#### B7. Iniciar Auto-Rig

Com o modelo sem rigless selecionado, clique em **Start Auto-Rig**. A captura de tela mostra o botão equivalente de Propriedades da Cena; o mesmo comando está na parte superior da guia Rig Builder da janela de visualização habilitada na etapa anterior.

![B7: Iniciar Auto-Rig](../images/rig-builder/en/b06-start-wizard.png)

*1 — Iniciar Auto-Rig.*

#### B8. Escolha a malha de entrada

Em `Select Mesh`, selecione o modelo e verifique a verificação da malha selecionada e clique em **Next**. Não escolha um widget ou outro objeto de visualização.

![B8: Escolha a malha de entrada](../images/rig-builder/en/b07-select-input.png)

*1 — Entrada do manequim. 2 — Próximo.*

#### B9. Escolha um body rig com ambos os métodos

Selecione **Body Only** e `Kinematics: IK + FK`. Mantenha**Generate Control Shapes** ativado. Clique em**Next**. Este manequim cápsula não possui topologia facial, portanto Corpo + Rosto é desnecessário.

![B9: Escolha um body rig com ambos os métodos](../images/rig-builder/en/b08-body-ikfk.png)

*1 — Somente Corpo. 2 — IK + FK. 3 — Próximo.*

#### B10. Detectar marcadores corporais iniciais

Em Marcadores Corporais, clique em **Detect Markers** em Detecção Inteligente. Trate suas suposições como ponto de partida. Mantenha**Mirror Symmetry** ativado para este modelo simétrico. Não aceite todas as suposições sem verificá-las.

![B10: Detectar marcadores corporais iniciais](../images/rig-builder/en/b09-detect-markers.png)

*1 — Detectar marcadores. 2 — Simetria do Espelho.*

#### B11. Revise as posições detectadas

Verifique o topo da cabeça, a base do pescoço, a pélvis, os punhos e os tornozelos contra a malha visível. Esta visualização segmentada produz várias suposições de baixa confiança. Revise e corrija os pontos de referência principais e os pontos de referência de precisão opcionais antes de gerar. Os rótulos de confiança descrevem a detecção original; uma marca verde no início de uma linha indica que o posicionamento atual foi confirmado.

![B11: Revise as posições detectadas](../images/rig-builder/en/b10-review-markers.png)

*1 — Resumo de confiança de detecção. 2 — Linhas de marcadores corporais.*

#### B12. Coloque um punho na malha

Na guia da janela de visualização **Rig Builder**, clique no conta-gotas**Place Marker** em Pulso Esquerdo e, em seguida, clique na superfície do punho na janela de visualização. Para um marcador já confirmado, redefina essa linha primeiro para expor seu botão de posicionamento. Na vista frontal, o punho esquerdo do personagem está à direita da tela.

![B12: Coloque um punho na malha](../images/rig-builder/en/b11-place-wrist.png)

*1 — Controle de posicionamento do punho esquerdo. 2 — Clique na superfície do punho.*

#### B13. Verifique o punho e tornozelos espelhados

Verifique se ambas as fileiras de punhos agora mostram marcas verdes e coordenadas X opostas. Repita a colocação para `Ankle Left`; simetria fornece tornozelo direito. Coloque cada tornozelo na articulação, não no dedo do pé. Verifique a simetria em relação à malha em vez de copiar as coordenadas do exemplo em um caractere de tamanho diferente.

![B13: Verifique o punho e tornozelos espelhados](../images/rig-builder/en/b12-mirrored-wrist.png)

*1 — Par de punho confirmado. 2 — Pulso espelhado na malha.*

#### B14. Refine ombros e cotovelos

Role até Marcadores de precisão. Reinicie e coloque `Shoulder Left` na articulação do braço e `Elbow Left` na abertura do cotovelo. Confirme seus parceiros espelhados. Mantenha o punho na extremidade do antebraço. Esses pontos determinam a cadeia do braço, portanto, um ombro ou cotovelo adivinhado na cápsula errada precisa de correção.

![B14: Refinar ombros e cotovelos](../images/rig-builder/en/b13-arm-precision.png)

*1 — Linhas marcadores de ombros e cotovelos. 2 – Ombro. 3 — Cotovelo.*

#### B15. Refine quadris e joelhos

Coloque `Hip Left` na parte superior da coxa e `Knee Left` na abertura da coxa/canela. Verifique o lado oposto fornecido por simetria. Mantenha a pélvis na linha central, entre os quadris.

![B15: Refinar quadris e joelhos](../images/rig-builder/en/b14-leg-precision.png)

*1 — Remadas de quadril e joelho. 2 — Superfície do quadril. 3 – Abertura do joelho.*

#### B16. Verifique a profundidade e os dedos dos pés lateralmente

Pressione `Numpad 3` com o ponteiro sobre a janela de visualização. Verifique os pontos de referência na ortografia direita e também na frente. Coloque `Toe Left` próximo à frente do pé; verifique seu parceiro espelhado. Um marcador pode parecer correto visto de frente, mas estar muito à frente ou atrás do corpo.

![B16: Verifique a profundidade e os dedos do lado](../images/rig-builder/en/b15-side-depth.png)

*1 — Ortográfica Direita. 2 — Linha marcadora do dedo do pé. 3 — Superfície do pé.*

#### B17. Coloque os calcanhares

Redefina um calcanhar adivinhado incorretamente e coloque `Heel Left` próximo à parte de trás do pé, na vista lateral. Verifique o calcanhar certo. Embora esses marcadores sejam opcionais, deixar ambos em zero produziu um aviso de proximidade na versão testada. Colocá-los nos pés eliminou esse aviso.

![B17: Coloque os calcanhares](../images/rig-builder/en/b16-place-heels.png)

*1 — Par de salto confirmado. 2 — Localização do calcanhar.*

#### B18. Confirme e continue

Revise o topo da cabeça, a base do pescoço e a pélvis, bem como todos os pontos de referência emparelhados. Clique em **Confirm All Placed** e depois em**Next**. As marcas verdes ao lado dos nomes representam o estado de confirmação; os rótulos de confiança REVIEW/ADJUST originais podem permanecer visíveis em 9.1.2.

![B18: Confirme e continue](../images/rig-builder/en/b17-confirm-markers.png)

*1 — Confirme tudo colocado. 2 — Próximo.*

#### B19. Pule os dedos para esta malha

Escolha `0 — No Fingers` e clique em **Next**. Este manequim possui cápsulas para as mãos, mas não possui geometria para os dedos. Em uma malha manual real, escolha a contagem apropriada e coloque os marcadores dos dedos.

![B19: Pule os dedos para esta malha](../images/rig-builder/en/b18-no-fingers.png)

*1 — Sem dedos. 2 — Próximo.*

#### B20. Revise e gere

Exija **All checks passed** antes de continuar. Use**IK + FK**, formas de controle ativadas, `Spine Segments: 3`, `Neck Segments: 1`, `No Fingers` e**Game Ready** para este exercício. Desligue os ossos torcidos, os ossos da saia, preservar o volume e os corretivos de articulações. Clique em**Generate Rig**. Essas configurações descrevem esse manequim de treinamento simples, e não uma prescrição universal de exportação.

![B20: Revise e gere](../images/rig-builder/en/b19-review-generate.png)

*1 — Verificações de marcadores. 2 — Configurações de geração. 3 — Gerar rig.*

#### B21. Crie os controles do animador

Após a geração, clique em **Build Control Rig**. Generate Rig fornece o rig da carroceria e pesos; Build Control Rig adiciona a camada de controle usada abaixo. Não clique em Quick Mannequin novamente – a malha de entrada já está presente, mesmo que o painel de conclusão exiba sua oferta genérica de manequim.

![B21: Construa os controles do animador](../images/rig-builder/en/b20-build-controls.png)

*1 — Construir rig de controle.*

#### B22. Conclua o assistente

Aguarde a mensagem de conclusão do rig de controle e clique em **Close Wizard**. A nova armadura aparece no Outliner. Mantenha o antigo metarig Simple Human escondido. A nova rig deve deformar a malha; apenas ver ossos na janela de visualização não é validação suficiente.

![B22: Conclua o assistente](../images/rig-builder/en/b21-close-wizard.png)

*1 — O botão Construir agora está desativado. 2 — Fechar assistente.*

### Parte C: Teste de pesos e uso IK/FK

A armadura gerada possui este nome de objeto na versão testada (use-o no Outliner e na ferramenta de peso):

```text
BoneForge_Rig
```

`FK (Forward Kinematics)` **FK (cinemática direta)** transmite as rotações pela hierarquia: gire o braço, depois o antebraço e depois a mão. É adequada para movimentos amplos e membros livres. `IK (Inverse Kinematics)`**IK (cinemática inversa)** parte de uma extremidade: mova o alvo do punho ou do tornozelo e o solver flexiona a cadeia para alcançá-lo. É adequada para pés apoiados e mãos que precisam alcançar uma superfície.

|Tarefa|Controle para usar|O que assistir|
|---|---|---|
|Balançar um braço|FK controles de ombro e cotovelo|Os controles infantis seguem seus pais|
|Coloque uma mão|Alvo de punho IK |Ombro e cotovelo resolvem em direção ao alvo|
|Plante um pé|Alvo de tornozelo IK para essa perna|Mova o corpo enquanto o alvo alcançável permanece no lugar|
|Aponte uma flexão de cotovelo ou joelho|Controle de pólo IK |O poste define a direção da curvatura; não é o alvo do punho/tornozelo|
|Método de mudança|Os botões IK/FK do membro|Verifique a pose tirada antes de digitar a animação|

O exercício abaixo compara um braço em ambos os modos. Cada membro tem seu próprio interruptor. `Bake IK / Bake FK` são ferramentas de conversão de animação; um interruptor de pose única não substitui o cozimento ou a codificação de uma animação. Consulte [Camada de controle](05-rig-tools.md#control-layer-camada-de-controle-ikfk) para os outros controles.

#### C1. Abra a camada de controle

Selecione **armadura gerada**, escolha**Pose Mode** e abra**BoneCraft → Review → Control Layer**. Há um interruptor IK/FK separado para cada braço e perna. Comece com**arm-L → FK**. Esquerda e direita referem-se ao personagem, então arm-L aparece à sua direita na vista frontal.

![C1: Abra a camada de controle](../images/rig-builder/en/c02-control-layer.png)

*1 — Modo de pose. 2 — Camada de controle e chave arm-L.*

#### C2. Mostrar os controles do animador

Abra **Object Data Properties → Bone Collections** da armadura. Use as estrelas Solo para `Controls` e**FK** para isolar suas formas de controle. Ative**In Front** em Exibição da viewport quando os controles estiverem obscurecidos pela malha. Posteriormente, inclua**IK** ao usar destinos. Esta lista de coleções nativas também funciona se o painel Coleções BoneCraft falhar ao desenhar neste host.

![C2: Mostrar os controles do animador](../images/rig-builder/en/c03-visible-controls.png)

*1 — Controles e estrelas FK Solo. 2 — Na Frente.*

#### C3. Selecione o controle FK do antebraço

Na vista frontal, clique no controle circular no cotovelo esquerdo do personagem. Verifique se o nome da seleção da janela de visualização é **forearm.fk-L**. Um controle de antebraço FK gira em torno do cotovelo; selecionar o controle do ombro giraria o braço e seus filhos.

![C3: Selecione o controle FK do antebraço](../images/rig-builder/en/c04-select-fk.png)

*1 — Controle antebraço.fk-L selecionado. 2 — FK está ativo para arm-L.*

#### C4. Gire e inspecione a deformação

Gire o controle FK selecionado sobre o **Y** global, aproximadamente `−45°` para este exemplo de vista frontal. Use a ferramenta Girar; no mapa de teclado Bforartists mostrado,**Ctrl+E**,**Y**, digite**-45**, então**Enter** executa essa rotação. O atalho de rotação padrão de Blender é**R**. A captura de tela mostra deliberadamente o problema inicial do peso: a cápsula do braço inclina-se com o antebraço. Não aceite isso como um rig acabado.

![C4: Gire e inspecione a deformação](../images/rig-builder/en/c05-fk-weight-check.png)

*1 — Movimento incorreto do braço durante o teste FK.*

#### C5. Recalcular os pesos do manequim

Se o teste de pose acima falhar, mude para **Object Mode**, selecione a malha e abra**BoneCraft → Skin → Weight Tools → Automatic Bone Weight Recalculation**. Defina Mesh como Reweight para o manequim e Existing Armature para**armadura gerada**. Escolha**Body**, `Body Method: Bone Heat`, `New Weight Strength: 1.00`, `Smooth Passes: 0`, `Max Bones per Vertex: 0` e `Minimum Weight: 0.001`. Mantenha**Keep Weight Backup** ativado e execute**Automatic Bone Weight Recalculation**. Isso reparou a visualização segmentada na versão testada.

![C5: Recalcular os pesos do manequim](../images/rig-builder/en/b23-recalculate-weights.png)

*1 — Malha e armadura. 2 - Calor Osso. 3 — Configurações de substituição e backup. 4 — Recalcular.*

#### C6. Verifique a curva FK reparada

Selecione novamente a armadura gerada e retorne para **Pose Mode**. O braço agora deve permanecer na horizontal do ombro ao cotovelo enquanto o antebraço sobe a partir do cotovelo. O objeto `WEIGHTS_BACKUP_…` oculto preserva os pesos antigos. Teste outros membros também antes de usar seu próprio personagem na animação. Um esqueleto gerado por si só não é prova de esfola correta.

![C6: Verifique a dobra FK reparada](../images/rig-builder/en/c05-fk-result.png)

*1 — O braço permanece no lugar. 2 — Antebraço dobrado na altura do cotovelo.*

#### C7. Mude o mesmo braço para IK

Clique em **arm-L → IK**. A chave coloca o alvo na pose atual, de modo que o braço deve permanecer na pose levantada. Adicione**IK** às coleções Solo visíveis se seus alvos estiverem ocultos. Mudanças de comutação que controlam a corrente; isso não significa que uma nova animação foi gravada.

![C7: Mude o mesmo braço para IK](../images/rig-builder/en/c06-switch-ik.png)

*1 — interruptor arm-L IK. 2 — Postura mantida ao trocar.*

#### C8. Selecione o alvo de punho IK

Clique no controle no punho e verifique o nome da seleção **forearm.ik-L**. Apesar do nome do antebraço, este é o alvo final da cadeia de braço. Mova este alvo para colocar a mão; o solucionador altera os ângulos dos ombros e cotovelos para alcançá-lo.

![C8: Selecione o alvo de punho IK](../images/rig-builder/en/c07-select-ik.png)

*1 — Alvo de punho selecionado. 2 — Nome da seleção.*

#### C9. Mova o alvo e compare

Mova o alvo do punho ligeiramente para dentro ao longo do **X** global. Neste exemplo, `−0.15 m` cria uma dobra visivelmente diferente. No mapa de teclado mostrado, use**Ctrl+W**,**X**, digite `-0.15` e, em seguida,**Enter** ou arraste a seta X da ferramenta Mover. O atalho de movimento padrão de Blender é**G**. Compare o braço inteiro com o exemplo FK: os terminais da extremidade e ambos os segmentos do braço seguem. Mantenha o alvo ao alcance do braço.

![C9: Mova o alvo e compare](../images/rig-builder/en/c08-move-ik.png)

*1 — Ponto final do punho. 2 — A cadeia responde. 3 — Exemplo de movimento X.*

#### C10. Volte e salve o exemplo

Clique em **arm-L → FK** novamente. Os controles FK se ajustam à pose IK atual. Verifique se a malha não salta e use**File → Save As** para salvar `Mannequin_AutoRig.blend`. A captura de tela mostra o exemplo salvo com FK ativo. Para uma cópia de treinamento neutra, mantenha todos os quatro membros em FK, selecione todos os controles de pose visíveis e use**F3 → Clear Pose Transforms → All** como na Parte A; salve isso com um nome separado.

![C10: Volte e salve o exemplo](../images/rig-builder/en/c10-save-complete.png)

*1 — FK ativo novamente. 2 — Postura preservada. 3 — Nome do arquivo salvo.*

**Verificação de conclusão:** você preservou a visualização original do metarig, desanexou um manequim sem rig, gerou um novo body rig e seus controles, corrigiu os pesos de visualização e comparou uma rotação FK com um movimento de destino IK. Mantenha o rig salvo como exemplo de aprendizado; substitua a visualização pela geometria de caracteres adequada para produção.

---

### Redirecionamento de animação

Mover a animação de um esqueleto para outro é abordado em [Ferramentas de rig: redirecionamento](05-rig-tools.md#redirecionar).

---

## Mesclagem de Ossos

**O que faz:** Combina duas armaduras em uma — por exemplo, um rig para o corpo e um para roupas ou cabelo — mantendo todos os pesos.

[Guia 11](03-guides-b.md#guia-11-junte-dois-rigs) percorre isso passo a passo.

**As três etapas:**
1. Escopo — escolha as duas armaduras e analise como elas diferem
2. Renomear — resolva conflitos de nomes e marque novos ossos
3. Mesclar – visualize e depois mescle

**Controles principais:**
- **Base** — a armadura que permanece; a outra armadura se funde com ela e fica então oculta
- **Analyze** — compara os dois esqueletos;**Acknowledge Scope — Proceed to Rename** abre o estágio 2
- **Normalize Both Armatures** — renomeia os ossos padrão de ambos os rigs para um padrão de nomenclatura (Mixamo Prefixed, Mixamo Stripped ou customizado)
- **Auto-Propose Renames** — sugere nomes para os próprios ossos da rig de fusão
- **Apply Rename** — renomeia uma entrada (uma etapa de desfazer);**Apply Batch Pattern** renomeia muitos com um padrão (com `{bone}`, `{side}` e `{index}` )
- **Mark as Unique** — mantém um osso como um novo osso em vez de mesclá-lo
- **Verify Rename — Proceed to Merge** — abre o estágio 3
- **Run Merge Preview** — relata o que a mesclagem faria, sem alterar nada
- **Merge Armatures** — faz backup de ambas as armaduras e as mescla

**Onde encontrar:** Guia BoneCraft → Mesclar ossos

Próximo: [Mecanismos](07-mechanisms.md)
