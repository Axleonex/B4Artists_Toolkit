# Ferramentas de rig

[← Conteúdo](index.md)

Este capítulo aborda detalhadamente as ferramentas de rigging, animação e peso do BoneCraft. Use-o quando quiser entender um recurso mais profundamente ou quando os guias não cobrirem sua situação exata.

Cada entrada diz o que a ferramenta faz, quando você a usaria, seus principais controles e onde encontrá-la. A linha "Onde encontrá-lo" de cada entrada nomeia o modo necessário para usá-lo: por exemplo, controles de rig no modo Pose, espelho de peso e transferência de peso no modo Weight Paint e Delta Mush no modo Object. Algumas seções permanecem visíveis com uma mensagem sobre o que selecionar quando suas ferramentas não podem ser executadas.

Na versão 9.1, muitas ferramentas são executadas ao mesmo tempo e colocam suas opções no painel Ajustar última operação. Altere essas opções imediatamente após o clique, antes de executar outra operação. Os menus Pose → BoneCraft e Pesos → BoneCraft e os painéis de botões BoneCraft nas guias Pose e Weights Tool Shelf do Bforartists oferecem atalhos para operações comuns. [Primeiros passos](01-start.md#onde-fica-cada-coisa) lista esses pontos de acesso.

---

## Ferramentas de interface de rig

Essas ferramentas ajudam você a gerenciar o lado visual do trabalho com armaduras — quais ossos são visíveis, como estão organizados e acesso rápido.

---

### Coleções de ossos

**O que faz:** Mostra as coleções de ossos do seu esqueleto como linhas. Clique no nome de uma coleção para selecionar seus ossos; o ícone do olho mostra ou oculta.

> Uma coleção de ossos é um grupo nomeado de ossos — por exemplo, "IK Controls", "Face Bones" e "Deform Bones". Ocultar uma coleção oculta esses ossos na janela de visualização, para que você possa focar em uma parte do rig.

**Controles principais:**
- Cada linha: a cor de destaque, **Toggle Collection Visibility** (ícone de olho), o nome da coleção (seleciona seus ossos),**Solo Collection** e**Rename Collection Display**, que define um nome de exibição personalizado para a linha. Passe o mouse sobre um botão somente de ícone para identificá-lo pela dica de ferramenta
- **Show All Collections** e**Hide All Collections** (ícones de olhos abertos e fechados acima da lista) — tudo de uma vez
- Seções — agrupe várias coleções em um cabeçalho recolhível

**Onde encontrar:** Guia BoneCraft → Revisão → Coleções

---

### Marcadores de Visibilidade

**O que faz:** Salva quais coleções de ossos estão visíveis, para que você possa alternar entre as visualizações salvas de uma só vez.

**Exemplo de uso:** Você configura uma visualização apenas com os ossos da face para trabalho de expressão e salva-a como "Somente Face". Aí você mostra tudo para pintura de peso e salva como "Full Rig". Agora um clique alterna entre eles.

**Controles principais:** cada slot é uma linha.
- O nome do marcador — clique nele para aplicar a visualização salva
- **Save Bookmark** — salva a visibilidade atual no slot; passe o mouse sobre seu ícone para ver a dica de ferramenta
- A amostra de cores – codifica o marcador com cores
- **Clear Bookmark** e**Remove Bookmark** (ícones de fechamento) — esvazie o slot ou remova um adicionado
- **Add Bookmark** — adiciona um slot

**Marcadores padrão:** FK Arms, IK Body, Face Only, Full Rig

**Onde encontrar:** Guia BoneCraft → Revisão → Coleções → Marcadores de visibilidade

---

### Painel rápido por atalho

**O que faz:** Abre o painel de rig do BoneCraft (coleções e marcadores) como um pop-up onde quer que seu cursor esteja.

**Como usar:** Pressione**Ctrl+Shift+R** na janela de visualização 3D. Clique fora do pop-up para fechá-lo.

**Onde encontrar:** o atalho**Ctrl+Shift+R** na janela de visualização 3D (não possui painel próprio)

---

## Ferramentas de animação

---

### Biblioteca de Poses

**O que faz:** Armazena poses nomeadas com miniaturas que você pode aplicar ao seu rig com um clique.

**Controles principais:**
- **Save** — armazena as posições atuais dos ossos como uma pose nomeada, com uma miniatura da janela de visualização
- **Apply** — ajusta os ossos à pose salva
- **Blend** — aplica a pose com força parcial, misturada com a posição atual
- **Mirror** — aplica a pose invertida da esquerda para a direita
- **Delete**,**Rename** e**Category** — gerenciam a lista;**Filter** mostra uma categoria
- **Export** e**Import** — salve ou carregue de um arquivo `.bfpose`

A mistura aplica-se imediatamente. Defina a intensidade da mesclagem em Ajustar última operação após clicar nele.

**Onde encontrar:** Guia BoneCraft → Revisão → Biblioteca de poses

---

### Control Picker (seletor de controles)

**O que faz:** Um mapa clicável dos controles do seu rig. Clique em uma forma para selecionar seu osso; o seletor destaca o que está selecionado.

**Controles principais:**
- **Generate Picker** — cria o layout a partir do seu rig
- **Edit Layout** — mova, redimensione e reetiquete os controles (**Move Picker Control**,**Resize Picker Control** e**Relabel Picker Control** aparecem como ícones na linha de cada controle) e**Snap** os em uma grade;**Rebuild Layout** constrói novamente
- **Mirror Selection** — seleciona os controles espelhados
- **Pop-up Picker** — abre o seletor em uma janela flutuante, que também possui**Add Selection Set**

**Onde encontrar:** Guia BoneCraft → Revisão → Seletor de controle

---

### Control Layer (camada de controle, IK/FK)

Para uma comparação prática ilustrada, siga [Teste pesos e use IK/FK](06-rig-builder.md#parte-c-teste-de-pesos-e-uso-ikfk).

**O que faz:** Controles do animador para os membros de um rig feito por**Build Control Rig**: alterne um membro entre IK e FK sem que o membro salte e coloque um no outro em um intervalo de quadros.

**Controles principais:**
- **IK** e**FK** – troque o membro e encaixe os novos controles no local onde o membro está, para que o cotovelo ou joelho não estale
- **Bake IK** e**Bake FK** — converte a animação em um intervalo de quadros para IK ou para FK
- **Pole Follow**,**Pin** e**Lock-Free** e**Global Rig Scale**, que mantém bloqueios protegidos

**Onde encontrar:** Guia BoneCraft → Revisão → Camada de controle (com um rig feito por**Build Control Rig** selecionado; consulte [Construtor de plataforma](06-rig-builder.md) )

---

### Ferramentas Rigify

**O que faz:** Detecta um rig de controle Rigify e conecta o painel de coleção, marcadores e controles deslizantes de propriedade do BoneCraft aos controles padrão do Rigify.

> Rigify é o sistema integrado do Bforartists para gerar rigs prontos para animação. Se você construiu seu rig com Rigify, isso conecta a IU do BoneCraft aos controles IK/FK do Rigify.

**Controles principais:**
- **Auto-Enhance** — configura os painéis do BoneCraft para o rig Rigify selecionado
- **Re-run Enhancement** – reconstrói-los do zero
- **Enable Rigify** está em Quick Rig; expanda sua seção de solução de problemas para**Generate Control Rig (active metarig)** (consulte [Construtor de plataforma](06-rig-builder.md) )
- Propriedades de Rigify - os controles deslizantes IK/FK, estiramento, espaço pai e cabeça/pescoço do rig

**Onde encontrá-lo:** Guia BoneCraft → Configurar Rigging → Ferramentas Rigify (e a seção Propriedades de Rigify )

---

### Redirecionar

**O que faz:** move a animação de um esqueleto para outro — por exemplo, um clipe de captura de movimento para o seu avatar. Os ossos são combinados por nome e direção, de modo que os membros mantêm sua orientação; as clavículas são folgadas para que os ombros não girem demais.

**Controles principais:**
- **Import Clip** e**Browse Library** — carregue um clipe ou defina uma pasta de biblioteca; clique no nome de um clipe para selecioná-lo
- **Auto-Match Bones** (a marca de seleção na linha de um clipe) — pares de ossos de origem e de destino (a lista Mapeamento de ossos do painel mostra os pares)
- **Preview** e**Stop Preview** – experimente o resultado
- **Apply** – grava o clipe em seu rig

**Onde encontrar:** Guia BoneCraft → Configurar Rigging → Retarget

---

### Shape keys corretivos

**O que faz:** Teclas de formato que são ativadas quando um osso atinge um ângulo, para corrigir beliscões ou colapsos em poses extremas.

**Exemplo de uso:** O cotovelo do seu personagem desmorona quando totalmente dobrado. Você esculpe um cotovelo corrigido e o vincula ao osso do braço para que ele seja aplicado automaticamente conforme o cotovelo dobra.

**Controles principais:**
- Novo Corretivo - escolha o **Shape Key**, o**Driver Bone**, o eixo de rotação, o ângulo no qual a forma está totalmente ativada e quão gradualmente ela desaparece, então**Create Corrective**
- A lista de corretivos: clique no nome da chave de forma de um corretivo para selecioná-lo; **Edit** e**Delete** na lista atuam no selecionado

A edição começa a partir dos valores atuais do corretivo. Altere seu ângulo e enfraquecimento em Ajustar última operação após clicar nele.

**Onde encontrar:** Guia BoneCraft → Skin → Corretivos (a malha precisa de uma chave de forma básica)

---

### Ferramentas de Gráfico

**O que faz:** Ferramentas de refinamento de animação para quadros-chave e curvas.

- **Interactive Breakdown** (Breakdowner; atalho**Ctrl+Shift+B** na janela de visualização 3D) — arraste para a esquerda e para a direita para mesclar a pose atual entre os quadros-chave mais próximos
- **Apply Delta** (Delta Mover; atalho**Ctrl+Shift+D** na janela de visualização 3D) — desloca os ossos selecionados por um deslocamento exato no espaço da tela ou no espaço mundial
- **Capture** e**Swap** (Buffer Curves) — mantenha uma cópia das curvas e troque entre elas e suas edições
- **Smart Bake** — cria animação baseada em restrições em chaves, descartando chaves redundantes (**Tol** define quanto)
- **Euler Filter** – corrige movimentos de rotação causados pelo bloqueio do gimbal
- Alças tangentes — defina os tipos de alças nas chaves selecionadas: **Auto**,**Vector**,**Aligned**,**Free** ou**Auto Clamped**

**Onde encontrar:** Guia BoneCraft → Revisão → Ferramentas gráficas

---

## Ferramentas de pesos

Essas ferramentas controlam como sua malha se deforma quando os ossos se movem. Os pesos informam a cada parte da malha quais ossos seguir e quanto.

---

### Recálculo automático de pesos de ossos

**O que faz:** recalcula os pesos de uma malha da rig existente, sem alterar a malha. Em malhas densas ele funciona através de uma malha proxy mais leve, portanto não falha silenciosamente.

**Controles principais:** escolha a malha e a armadura alvo e, em seguida, o modo Corpo ou Roupa. O corpo calcula os pesos da rig existente; A roupa os transfere de uma malha de origem corretamente ponderada. Defina o método, mesclagem e suavização, o número máximo de influências ósseas por vértice, um peso mínimo e se deseja manter um backup e, em seguida, execute**Automatic Bone Weight Recalculation**. Essas configurações estão acima do botão. O atalho CATS,**Smart Automatic Weights**, abre uma caixa de diálogo para a malha de destino, armadura e modo, além da malha de origem no modo Vestuário.

**Onde encontrar:** Guia BoneCraft → Pele → Ferramentas de Peso

---

### Espelho de Peso

**O que faz:** Copia pesos de um lado para o outro do seu avatar. Essencial para caracteres simétricos.

**Controles principais:**
- **Mirror All Weights** — espelha cada grupo ósseo para o lado oposto
- **Mirror Active Weight** — espelha apenas o grupo de ossos ativo
- Eixo de simetria e direção do espelho (nos dois sentidos, da esquerda para a direita ou da direita para a esquerda)
- **Topology Mirror** — emparelha vértices por topologia de malha em vez de posição
- **Search Distance** — quão distantes dois vértices podem estar e ainda contar como um par (aumente para malhas que não são perfeitamente simétricas)
- **Select Unmatched** — seleciona vértices sem parceiro;**Normalize Weights** soma os pesos para 1,0 depois

Clique primeiro em um botão de espelho e, em seguida, defina o eixo, a direção, o modo de topologia e a distância de pesquisa em Ajustar última operação. **Mirror Active Weight** também está em Pesos → BoneCraft e na guia Prateleira de ferramentas de pesos.

**Onde encontrar:** Guia BoneCraft, no modo Weight Paint → Weight Mirror

---

### Transferência de peso

**O que faz:** Copia pesos de uma malha de origem para a malha ativa. Usado para prender roupas ao corpo ou mover pesos de uma malha de alta resolução para uma inferior.

**Controles principais:**
- Escolha a malha de origem antes de transferir
- Após o clique, defina o método de transferência e filtro ósseo em Ajustar Última Operação
- **Normalize** em Ajustar última operação - mantém a soma dos pesos em 1,0
- **Transfer Weights** — executa; o resultado mostra a distância média e máxima, e**Select Problem Vertices** seleciona vértices que não correspondem

**Onde encontrar:** Guia BoneCraft, no modo Weight Paint → Weight Transfer (também em Skin → Weight Tools)

---

### Tabela de Pesos

**O que faz:** Mostra os pesos exatos do vértice selecionado para cada osso e permite definir um valor preciso.

**Como usar:** Selecione um vértice no modo Weight Paint; a tabela lista seus ossos e pesos. Clique no ícone de mão na linha de um osso e defina**Weight** em Ajustar última operação. Adicionar Influência usa o osso que você escolher; defina seu novo peso também em Ajustar última operação. Com vários vértices selecionados,**Normalize All Vertices** normaliza todos eles.

**Onde encontrar:** Aba BoneCraft, no modo Weight Paint → Tabela de Pesos

---

### Preenchimento por Inundação

**O que faz:** Define o peso do grupo ativo nos vértices selecionados com um clique:**Flood to 0.0**,**Flood to 1.0** ou**Flood to Custom**. Após Flood como Personalizado, defina**Value** e**Normalize** em Ajustar última operação. O menu e a estante Pesos chamam os botões de valor fixo Flood to Zero e Flood to One.

**Onde encontrar:** Aba BoneCraft → Pele → Ferramentas de peso; também Pesos → BoneCraft e Prateleira de Ferramentas → Pesos → BoneCraft

---

### Deformar vs Controlar

**O que ele faz:** Classifica os ossos do rig em ossos deformados (eles movem a malha) e ossos de controle (o animador os move), marca ossos deformados, renomeia-os para uma nomenclatura deformada e exporta um esqueleto somente deformado.

**Onde encontrar:** Aba BoneCraft, no Modo Pose → Deformar vs Controle

---

### Delta Mush

**O que faz:** Uma deformação suavizante que reduz a compressão nas articulações. A malha mantém sua forma em repouso, mas se deforma de maneira mais limpa em movimento.

**Como usar:** Clique em**Add Delta Mush** para adicionar o modificador e vinculá-lo à forma restante. Imediatamente depois, defina**Iterations**,**Smooth Strength**,**Pin Borders** e**Only Smooth Deform** em Ajustar última operação. Assim que o modificador existir, o painel mostrará**Rebind** e**Remove**, com uma pasta Configurações contendo as iterações do modificador, força de suavização e controles de fixação de borda.

**Onde encontrar:** Aba BoneCraft, no Modo Objeto com uma malha selecionada → Delta Mush

---

### Envolvimento por Proximidade

**O que faz:** Faz uma malha seguir a superfície da outra, como uma segunda pele. Útil para roupas que abraçam o corpo.

**Como usar:** selecione a malha de destino, escolha um**Driver Mesh** diferente e clique em**Bind Proximity Wrap**. Mantenha a armadura do motorista em posição de repouso durante a amarração. As opções dobradas abaixo do botão listam**Falloff Type** e**Max Distance**; em 9.1.2 esses valores são armazenados com a configuração, mas não alteram sua ligação Surface Deform. Uma vez vinculado, o painel mostra**Rebind** e**Unbind**. Desvincular desabilita o modificador na viewport e na renderização; isso não o remove.

**Onde encontrar:** Aba BoneCraft, no Modo Objeto com uma malha selecionada → Envolvimento de Proximidade

---

## Controles de rig

Essas ferramentas aparecem na guia BoneCraft no modo Pose.

---

### Troca de Espaço

**O que faz:** Altera o espaço que um osso segue durante a animação. Uma mão segurando um adereço pode passar de seguir o corpo para ficar parada no mundo com um clique.

**Controles principais:**
- **Add Space** e**Remove Space** (ícone X em Gerenciar Espaços) — os espaços que um osso pode seguir (Mundo, Origem ou outro osso)
- Um botão por espaço, com o seu nome; o espaço atual está marcado como ●. Clique no botão de outro espaço para mudar o osso para ele

**Onde encontrar:** Aba BoneCraft, no Modo Pose → Space Switch

---

### Spline IK

**O que faz:** Faz uma cadeia de ossos seguir uma curva. Usado para caudas, tentáculos, cordas, cabelos longos e espinhos que precisam de movimentos suaves e abrangentes.

**Como usar:** Ative o osso inicial e clique em**Generate Spline IK**. Defina**Chain Length**,**Curve Resolution**,**Stretch** e**Volume Preservation** em Ajustar a última operação.**Remove Spline IK** remove a configuração.

**Onde encontrar:** Aba BoneCraft, no Modo Pose → Spline IK

---

### Dinâmica de Cadeia

**O que faz:** Movimento secundário semelhante ao da física em uma cadeia óssea: os ossos ficam para trás quando o pai se move e saltam para trás quando ele para. Usado para fios de cabelo, caudas e acessórios.

**Como usar:** selecione a cadeia óssea e clique em**Add Chain Dynamics**. Defina**Stiffness**,**Damping**,**Mass** e**Gravity Scale** em Ajustar a última operação. O painel também lista os parâmetros em uma dobra Configurações abaixo da ação. Assim que existir dinâmica, ele mostra**Bake** e**Remove**. A colisão utiliza uma forma de esfera simplificada, portanto as superfícies côncavas podem não colidir corretamente.

**Onde encontrar:** Aba BoneCraft, no Modo Pose → Chain Dynamics

---

### Fita

**O que faz:** Constrói uma fita de Bendy Bones – ossos que se curvam e torcem suavemente – para lábios, sobrancelhas, cintos e outras áreas curvas suaves.

**Como usar:** Selecione a cadeia óssea e clique em**Generate Ribbon**, depois defina**Control Bones** e**Ribbon Width** em Ajustar última operação.**Remove Ribbon** remove a configuração.

**Onde encontrar:** Guia BoneCraft, no Modo Pose → Faixa de opções

---

### Biblioteca de Visemas

**O que faz:** cria e gerencia conjuntos de visemas (formatos de boca) vinculados a chaves de forma e gera chaves de sincronização labial a partir do texto. Para mapeamento de visema VRChat, use Mapeamento de visema VRChat; para gerar visemas do zero, use a seção CATS Visemas.

**Controles principais:**
- **New Set** e**Delete** — crie ou remova um conjunto de visema
- Em cada conjunto, um botão por visema (com um ícone de alto-falante) o visualiza
- Sincronização labial — texto para teclas de visema, com molduras por fonema e suavização

**Onde encontrar:** Aba BoneCraft, com uma armadura selecionada → Biblioteca Viseme

---

### Chave Conduzida por Conjunto

**O que faz:** Vincula um valor a outro sem expressões Python. Posicione o driver (por exemplo, um osso de sobrancelha), defina o valor acionado (por exemplo, uma chave de formato "Sobrancelha levantada") e registre o ponto; BoneCraft constrói a curva do driver.

**Controles principais:**
- **Driver Bone** e**Driver Attribute** – o que impulsiona
- **Target Bone** e**Target Attribute** – o que é acionado
- **Set Value** e**Record Point** — registre um ponto na curva
- **Create SDK** — cria o driver

**Onde encontrar:** Guia BoneCraft, no Modo Pose → Definir chave acionada

---

### Validador de Rig

**O que ele faz:** verifica seu rig em relação a um conjunto de regras e relata problemas — nomenclatura, ossos faltantes, restrições quebradas, hierarquia, pesos, drivers que precisam de Python e as regras dos mecanismos. Nomes de ossos com hífens (como `DEF-upper_arm.L` ) são aprovados.

**Controles principais:**
- **Run Validation** — executa todas as verificações e lista os resultados
- **Export Report** — salva os resultados em um arquivo

O Quadro de Tarefas (guia BoneCraft → Visão Geral → Quadro de Tarefas) mostra uma tarefa do validador quando uma verificação falha.

**Onde encontrar:** Guia BoneCraft → Revisão → Validador de rig

---

### Notas do Rig

**O que faz:** Notas escritas anexadas aos ossos da rig — o que você configura, lembretes, notas para colaboradores.

**Controles principais:** **Add Note** e**Remove** em cada nota. Rig Readme mostra as notas do rig como uma página somente leitura.

**Onde encontrar:** Guia BoneCraft → Visão geral → Notas e revisão da rig → Leiame da rig

Próximo: [Construtor de plataforma](06-rig-builder.md)
