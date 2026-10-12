# Construtor de Rig

[← Sumário](index.md)

## Construir um rig novo

O Construtor de Rig cria um rig novo para um personagem. Ele fica na sua própria aba **Rig Builder** da Tool Shelf da esquerda (pressione **T**), e sempre na aba **Cena** do editor de **Propriedades**. Em uma Tool Shelf estreita, ele muda para um layout compacto com rótulos curtos.

---

### Assistente Auto-Rig

**O que faz:** um guia passo a passo que posiciona marcadores na sua malha e constrói a partir deles um rig com pesos. É o jeito principal de fazer o rig de um personagem do zero.

O [guia 1](02-guides-a.md#guia-1-leve-seu-primeiro-avatar-para-o-vrchat) percorre o assistente passo a passo.

**Passos:** Selecionar malha → Tipo de rig → Marcadores do corpo → Marcadores dos dedos → Marcadores do rosto → Revisão → Gerar

**Controles principais:**
- **Iniciar Auto-Rig**, e **Voltar**, **Cancelar** e **Próximo** em cima e embaixo de cada passo
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

### Quick Rig (rig rápido)

**O que faz:** adiciona com um clique uma armadura pronta: o Basic Humanoid do BoneCraft (19 ossos, sem precisar do Rigify) ou um dos metarigs do Rigify. Mais rápido que o assistente, menos ajustado.

**Controles principais:**
- O botão Basic Humanoid e os metarigs do Rigify (**Habilitar Rigify** primeiro, se o Rigify estiver desativado)
- Opções para o próximo clique: **Ajustar Rig à Malha Ativa**, pesos automáticos, **Adicionar Controladores IK/FK** e **Pose Inicial**
- **T-Pose** e **Pose A** — trocar a pose de descanso do rig selecionado
- **Inspecionar Controles do Rig Ativo** e **Diagnosticar Rig Rápido (imprimir no console)** — verificar o que foi construído
- **Gerar Rig de Controle (metarig ativo)** — com um metarig do Rigify ativo, gera o rig de controle do Rigify dele

**A biblioteca de assets BoneCraft Rigs:** o Basic Humanoid também é um asset. Arraste-o da prateleira de assets para cima do seu personagem. Com o rig solto selecionado, o Quick Rig mostra "Dropped rig: fit it to a mesh" (rig solto: ajuste-o a uma malha): escolha a **Mesh** (malha), decida se vai ajustá-lo e dar pesos, e clique em **Fit Dropped Rig** (ajustar rig solto).

**Onde fica:** Rig Builder → Quick Rig

---

### Manequim

**O que faz:** constrói uma figura humana simples com rig, como substituta quando você ainda não tem um modelo. É só uma pré-visualização: troque-a pela sua própria malha antes do uso final.

**Controles principais:**
- **Manequim rápido** — constrói um com proporções padrão
- **Adicionar manequim** — constrói um com as configurações abaixo
- **Regenerar** e **Remover** — reconstruir com novas configurações, ou apagar junto com o rig
- **Modo**, **Tipo de corpo** e **Escala de raio**, com mais opções em Avançado

**Onde fica:** Rig Builder → Manequim

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

**Onde fica:** aba BoneCraft → Mesclagem de Ossos

Próximo: [Mechanisms (mecanismos)](07-mechanisms.md)
