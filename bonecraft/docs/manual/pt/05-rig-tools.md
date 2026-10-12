# Ferramentas de rig

[← Sumário](index.md)

Este capítulo explica em detalhes as ferramentas de rigging, animação e pesos do BoneCraft. Use-o quando quiser entender melhor um recurso, ou quando os guias não cobrirem exatamente a sua situação.

Cada entrada diz o que a ferramenta faz, quando usá-la, os controles principais e onde ela fica. Algumas ferramentas só aparecem em certo modo, e a linha "Onde fica" de cada entrada indica qual: por exemplo, os controles de rig no Modo Pose, o espelho e a transferência de pesos no modo Pintura de pesos, e o Delta Mush no Modo Objeto.

---

## Ferramentas de interface de rig

Estas ferramentas ajudam você a cuidar da parte visual do trabalho com armaduras: quais ossos aparecem, como estão organizados e um acesso rápido.

---

### Coleções de ossos

**O que faz:** mostra as coleções de ossos do seu esqueleto como linhas. Clique no nome de uma coleção para selecionar os ossos dela; o ícone de olho a mostra ou oculta.

> Uma coleção de ossos é um grupo de ossos com nome, por exemplo "IK Controls", "Face Bones" e "Deform Bones". Ocultar uma coleção oculta esses ossos na viewport, para você se concentrar em uma parte do rig.

**Controles principais:**
- Cada linha: a cor de destaque, **Toggle Collection Visibility** (alternar visibilidade; ícone de olho), o nome da coleção (seleciona os ossos), **Solo Collection** (coleção solo; ícone S) e **Rename Collection Display** (renomear exibição; ícone de engrenagem), que dá à linha um nome de exibição personalizado
- **Show All Collections** (mostrar todas as coleções) e **Hide All Collections** (ocultar todas as coleções) (ícones de olho aberto e fechado acima da lista) — tudo de uma vez
- Seções — agrupar várias coleções sob um cabeçalho recolhível

**Onde fica:** aba BoneCraft → Revisão → Coleções

---

### Marcadores de Visibilidade

**O que faz:** salva quais coleções de ossos estão visíveis, para você alternar de uma vez entre visualizações salvas.

**Exemplo de uso:** você prepara uma visualização só com os ossos do rosto para trabalhar expressões e a salva como "Face Only". Depois mostra tudo para pintar pesos e salva como "Full Rig". Agora um clique alterna entre as duas.

**Controles principais:** cada slot é uma linha.
- O nome do marcador — clique nele para aplicar a visualização salva
- **Save Bookmark** (salvar marcador; ícone de disco) — salva a visibilidade atual no slot
- A amostra de cor — dá uma cor ao marcador
- **Clear Bookmark** (limpar marcador) e **Remove Bookmark** (remover marcador; ícones de fechar) — esvaziam o slot ou removem um slot adicionado
- **Adicionar favorito** — adiciona um slot

**Marcadores padrão:** FK Arms, IK Body, Face Only, Full Rig

**Onde fica:** aba BoneCraft → Revisão → Coleções → Marcadores de Visibilidade

---

### Painel rápido por atalho

**O que faz:** abre o painel de rig do BoneCraft (coleções e marcadores) como janela suspensa onde estiver o cursor.

**Como usar:** pressione **Ctrl+Shift+R** na viewport 3D. Clique fora da janela para fechá-la.

**Onde fica:** o atalho **Ctrl+Shift+R** na viewport 3D (ele não tem painel próprio)

---

## Ferramentas de animação

---

### Biblioteca de Poses

**O que faz:** guarda poses com nome e miniatura que você aplica ao seu rig com um clique.

**Controles principais:**
- **Salvar** — guarda as posições atuais dos ossos como uma pose com nome, com uma miniatura da viewport
- **Aplicar** — leva os ossos à pose salva
- **Mesclar** — aplica a pose com intensidade parcial, misturada à posição atual
- **Espelhar** — aplica a pose invertida da esquerda para a direita
- **Excluir**, **Renomear** e **Categoria** — gerenciar a lista; **Filtro** mostra uma só categoria
- **Exportar** e **Importar** — salvar em um arquivo `.bfpose` ou carregar de um

**Onde fica:** aba BoneCraft → Revisão → Biblioteca de Poses

---

### Control Picker (seletor de controles)

**O que faz:** um mapa clicável dos controles do seu rig. Clique em uma forma para selecionar o osso dela; o seletor destaca o que está selecionado.

**Controles principais:**
- **Generate Picker** (gerar seletor) — monta o layout a partir do seu rig
- **Edit Layout** (editar layout) — mover, redimensionar e renomear os controles (**Move Picker Control** (mover controle), **Resize Picker Control** (redimensionar controle) e **Relabel Picker Control** (renomear controle) aparecem como ícones na linha de cada controle) e alinhá-los a uma grade com **Snap** (encaixar); **Reconstruir Layout** o monta de novo
- **Espelhar Seleção** — seleciona os controles do lado espelhado
- **Seletor Pop-up** — abre o seletor em uma janela flutuante, que também tem **Add Selection Set** (adicionar conjunto de seleção)

**Onde fica:** aba BoneCraft → Revisão → Control Picker

---

### Control Layer (camada de controle, IK/FK)

**O que faz:** controles de animador para os membros de um rig construído por **Construir Rig de Controle**: trocar um membro entre IK e FK sem que ele salte, e fazer o bake de um no outro ao longo de um intervalo de quadros.

**Controles principais:**
- **IK** e **FK** — trocam o membro e encaixam os novos controles onde o membro está, para que o cotovelo ou o joelho não saltem
- **Bake IK** (bake para IK) e **Bake FK** (bake para FK) — convertem a animação para IK ou para FK em um intervalo de quadros
- **Pole Follow** (acompanhar o polo), **Pin** (fixar) e **Lock-Free** (sem trava), e **Global Rig Scale** (escala global do rig), que mantém as travas protegidas

**Onde fica:** aba BoneCraft → Revisão → Control Layer (com um rig construído por **Construir Rig de Controle** selecionado; veja [Construtor de Rig](06-rig-builder.md))

---

### Ferramentas Rigify

**O que fazem:** detectam um rig de controle do Rigify e ligam o painel de coleções, os marcadores e os controles deslizantes de propriedades do BoneCraft aos controles padrão do Rigify.

> O Rigify é o sistema embutido do Bforartists para gerar rigs prontos para animar. Se você construiu seu rig com o Rigify, isto liga a interface do BoneCraft aos controles IK/FK do Rigify.

**Controles principais:**
- **Aprimoramento Automático** — configura os painéis do BoneCraft para o rig do Rigify selecionado
- **Executar Novamente o Aprimoramento** — reconstrói tudo do zero
- **Habilitar Rigify** e **Gerar Rig de Controle (metarig ativo)** ficam no Quick Rig (veja [Construtor de Rig](06-rig-builder.md))
- Propriedades Rigify — os controles deslizantes de IK/FK, alongamento, espaço pai e acompanhamento de cabeça/pescoço do rig

**Onde ficam:** aba BoneCraft → Configurar Rigging → Ferramentas Rigify (e a seção Propriedades Rigify)

---

### Redirecionar

**O que faz:** passa uma animação de um esqueleto para outro, por exemplo um clipe de captura de movimento para o seu avatar. Os ossos são associados por nome e por direção, então os membros mantêm a orientação; as clavículas são associadas de forma flexível para que os ombros não girem demais.

**Controles principais:**
- **Importar Clipe** e **Navegar na Biblioteca** — carregar um clipe, ou definir uma pasta de biblioteca; clique no nome de um clipe para selecioná-lo
- **Auto-Match Bones** (associar ossos automaticamente; a marca de verificação na linha de um clipe) — forma pares entre ossos de origem e de destino (a lista Mapeamento de Ossos do painel mostra os pares)
- **Pré-visualizar** e **Parar pré-visualização** — testar o resultado
- **Aplicar** — faz o bake do clipe no seu rig

**Onde fica:** aba BoneCraft → Configurar Rigging → Redirecionar

---

### Shape keys corretivos

**O que fazem:** shape keys que ligam quando um osso atinge um ângulo, para corrigir beliscões ou afundamentos em poses extremas.

**Exemplo de uso:** o cotovelo do seu personagem afunda quando dobrado por completo. Você esculpe um cotovelo corrigido e o liga ao osso do braço, para que ele se aplique sozinho conforme o cotovelo dobra.

**Controles principais:**
- Nova Correção — escolha o **Shape Key**, o **Osso Driver**, o eixo de rotação, o ângulo em que a forma fica totalmente ligada e quão gradualmente ela entra, e clique em **Criar Corretivo**
- A lista de corretivos: clique no nome do shape key de um corretivo para selecioná-lo; **Editar** e **Excluir**, abaixo da lista, agem sobre o selecionado

**Onde ficam:** aba BoneCraft → Skin → Corretivos (a malha precisa de um shape key base)

---

### Ferramentas de Gráfico

**O que fazem:** ferramentas de animação para refinar quadros-chave e curvas.

- **Divisão Interativa** (Breakdowner; atalho **Ctrl+Shift+B** na viewport 3D) — arraste para a esquerda e para a direita para misturar a pose atual entre os quadros-chave vizinhos
- **Aplicar Delta** (Movedor Delta; atalho **Ctrl+Shift+D** na viewport 3D) — desloca os ossos selecionados uma quantidade exata no espaço da tela ou do mundo
- **Capturar** e **Trocar** (Curvas em Buffer) — guardar uma cópia das curvas e alternar entre ela e suas edições
- **Assar Inteligente** — faz o bake em chaves da animação acionada por restrições, descartando chaves redundantes (**Tol** define quanto)
- **Filtro de Euler** — corrige viradas de rotação causadas pelo gimbal lock
- Alças Tangentes — definir o tipo de alça das chaves selecionadas: **Auto**, **Vector** (vetor), **Aligned** (alinhada), **Free** (livre) ou **Auto Clamped** (auto limitada)

**Onde ficam:** aba BoneCraft → Revisão → Ferramentas de Gráfico

---

## Ferramentas de pesos

Estas ferramentas controlam como sua malha se deforma quando os ossos se movem. Os pesos dizem a cada parte da malha quais ossos seguir, e quanto.

---

### Recálculo automático de pesos de ossos

**O que faz:** recalcula os pesos de uma malha a partir do rig existente, sem mudar a malha. Em malhas densas, trabalha por meio de uma malha proxy mais leve, para não falhar em silêncio.

**Controles principais:** a malha e a armadura de destino, o método, a mistura e a suavização, o número máximo de influências de ossos por vértice, um peso mínimo e um backup dos pesos antigos. Execute **Automatic Bone Weight Recalculation** (recálculo automático de pesos de ossos). A aba CATS tem um atalho: **Smart Automatic Weights** (pesos automáticos inteligentes).

**Onde fica:** aba BoneCraft → Skin → Ferramentas de Peso

---

### Espelho de Peso

**O que faz:** copia os pesos de um lado do seu avatar para o outro. Essencial para personagens simétricos.

**Controles principais:**
- **Espelhar Todos os Pesos** — espelha cada grupo de ossos para o lado oposto
- **Espelhar Peso Ativo** — espelha só o grupo de ossos ativo
- Eixo de simetria e direção do espelho (nos dois sentidos, da esquerda para a direita ou da direita para a esquerda)
- **Espelho de Topologia** — forma pares de vértices pela topologia da malha em vez da posição
- **Distância de Busca** — a que distância dois vértices podem estar e ainda contar como par (aumente para malhas que não são perfeitamente simétricas)
- **Selecionar Não Correspondentes** — seleciona vértices sem par; **Normalizar Pesos** faz em seguida os pesos somarem 1.0

**Onde fica:** aba BoneCraft, no modo Pintura de pesos → Espelho de Peso

---

### Transferência de peso

**O que faz:** copia os pesos de uma malha de origem para a malha ativa. Usada para prender roupas a um corpo, ou para passar pesos de uma malha de alta resolução para uma mais leve.

**Controles principais:**
- Malha de origem, método de transferência e filtro de ossos
- **Normalizar Após Transferência** — mantém a soma dos pesos em 1.0
- **Transferir Pesos** — executa; o resultado mostra a distância média e a máxima, e **Selecionar Vértices com Problema** seleciona os vértices que foram mal associados

**Onde fica:** aba BoneCraft, no modo Pintura de pesos → Transferência de peso (também em Skin → Ferramentas de Peso)

---

### Tabela de Pesos

**O que faz:** mostra os pesos exatos do vértice selecionado para cada osso, para você digitar valores precisos.

**Como usar:** selecione um vértice no modo Pintura de pesos; a tabela lista os ossos e pesos dele. Com vários vértices selecionados, **Normalizar todos os vértices** normaliza todos.

**Onde fica:** aba BoneCraft, no modo Pintura de pesos → Tabela de Pesos

---

### Preenchimento por Inundação

**O que faz:** define com um clique o peso do grupo ativo nos vértices selecionados: **Preencher com 0.0**, **Preencher com 1.0**, ou **Preencher** com um **Valor Personalizado** (com **Normalização Personalizada**).

**Onde fica:** aba BoneCraft → Skin → Ferramentas de Peso

---

### Deformar vs Controlar

**O que faz:** separa os ossos do rig em ossos de deformação (movem a malha) e ossos de controle (o animador os move), marca os ossos de deformação, dá a eles nomes de deformação e exporta um esqueleto só de deformação.

**Onde fica:** aba BoneCraft, no Modo Pose → Deformar vs Controlar

---

### Delta Mush

**O que faz:** uma deformação suavizante que reduz os beliscões nas articulações. A malha mantém a forma em repouso, mas se deforma de modo mais limpo em movimento.

**Controles principais:** iterações, força da suavização, bordas fixadas, suavizar só a deformação e se roda antes da armadura. O botão de adicionar coloca o modificador e o vincula à forma de repouso.

**Onde fica:** aba BoneCraft, no Modo Objeto com uma malha selecionada → Delta Mush

---

### Envolvimento por Proximidade

**O que faz:** faz uma malha acompanhar a superfície de outra, como uma segunda pele. Útil para roupas coladas ao corpo.

**Controles principais:** a malha condutora a acompanhar, o tipo de atenuação e a distância máxima; o botão de vincular prende a malha.

**Onde fica:** aba BoneCraft, no Modo Objeto com uma malha selecionada → Envolvimento por Proximidade

---

## Controles de rig

Estas ferramentas aparecem na aba BoneCraft no Modo Pose.

---

### Troca de Espaço

**O que faz:** muda o espaço que um osso segue durante a animação. Uma mão segurando um acessório pode passar com um clique de seguir o corpo para ficar parada no mundo.

**Controles principais:**
- **Adicionar Espaço** e **Remove Space** (remover espaço; ícone X em Gerenciar Espaços) — os espaços que um osso pode seguir (World, Origin ou outro osso)
- Um botão por espaço, com o nome dele; o espaço atual é marcado com ●. Clique no botão de outro espaço para trocar o osso para ele

**Onde fica:** aba BoneCraft, no Modo Pose → Troca de Espaço

---

### Spline IK

**O que faz:** faz uma cadeia de ossos seguir uma curva. Usado em caudas, tentáculos, cordas, cabelos longos e colunas que precisam de um movimento suave e amplo.

**Controles principais:** **Comprimento da Cadeia**, **Resolução de Curva**, **Esticar**, **Modo de Torção**, **Preservar Volume**; **Gerar Spline IK** e **Remover Spline IK**.

**Onde fica:** aba BoneCraft, no Modo Pose → Spline IK

---

### Dinâmica de Cadeia

**O que faz:** movimento secundário de tipo físico em uma cadeia de ossos: os ossos ficam para trás quando o pai se move e voltam quando ele para. Usado em mechas de cabelo, caudas e acessórios.

**Controles principais:** rigidez, amortecimento, massa e gravidade; adicionar dinâmica à cadeia selecionada. A colisão usa uma forma de esfera simplificada, então superfícies côncavas podem não colidir direito.

**Onde fica:** aba BoneCraft, no Modo Pose → Dinâmica de Cadeia

---

### Fita

**O que faz:** constrói uma fita de Bendy Bones (ossos que se curvam e torcem com suavidade) para lábios, sobrancelhas, cintos e outras áreas macias e curvas.

**Controles principais:** **Ossos de Controle** e **Largura da Fita**; **Gerar Fita** e **Remover Fita**.

**Onde fica:** aba BoneCraft, no Modo Pose → Fita

---

### Biblioteca de Visemas

**O que faz:** cria e gerencia conjuntos de visemas (formas de boca) ligados a shape keys, e gera chaves de sincronia labial a partir de texto. Para o mapeamento de visemas do VRChat, use o VRChat Viseme Mapping; para gerar visemas do zero, use a seção Visemas do CATS.

**Controles principais:**
- **Novo Conjunto** e **Excluir** — criar ou apagar um conjunto de visemas
- Em cada conjunto, um botão por visema (ícone de alto-falante) o pré-visualiza
- Sincronização Labial — de texto para chaves de visemas, com quadros por fonema e suavização

**Onde fica:** aba BoneCraft, com uma armadura selecionada → Biblioteca de Visemas

---

### Chave Conduzida por Conjunto

**O que faz:** liga um valor a outro sem expressões de Python. Faça a pose do condutor (por exemplo um osso de sobrancelha), defina o valor conduzido (por exemplo um shape key "Brow Raised") e registre o ponto; o BoneCraft constrói a curva do driver.

**Controles principais:**
- **Osso Driver** e **Atributo do Driver** — o que conduz
- **Osso Alvo** e **Atributo Alvo** — o que é conduzido
- **Definir Valor** e **Registrar Ponto** — registrar um ponto na curva
- **Criar SDK** — constrói o driver

**Onde fica:** aba BoneCraft, no Modo Pose → Chave Conduzida por Conjunto

---

### Validador de Rig

**O que faz:** confere seu rig com um conjunto de regras e informa os problemas: nomes, ossos faltando, restrições quebradas, hierarquia, pesos, drivers que precisam de Python e as regras de Mechanisms. Nomes de ossos com hífens (como `DEF-upper_arm.L`) passam.

**Controles principais:**
- **Executar validação** — executa cada verificação e lista os resultados
- **Export Report** (exportar relatório) — salva os resultados em um arquivo

O Quadro de Tarefas (aba BoneCraft → Visão Geral → Quadro de Tarefas) mostra uma tarefa do validador quando uma verificação falha.

**Onde fica:** aba BoneCraft → Revisão → Validador de Rig

---

### Notas do Rig

**O que fazem:** notas escritas presas aos ossos do rig: o que você configurou, lembretes, notas para colaboradores.

**Controles principais:** **Adicionar Nota**, e **Remover** em cada nota. Leia-me do Rig mostra as notas do rig como uma página somente leitura.

**Onde ficam:** aba BoneCraft → Visão Geral → Notas do Rig, e Revisão → Leia-me do Rig

Próximo: [Construtor de Rig](06-rig-builder.md)
