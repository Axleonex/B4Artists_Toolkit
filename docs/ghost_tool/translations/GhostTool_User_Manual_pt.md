# Ghost Tool 4.3.1: manual do usuário

Tradução do [manual em inglês 4.3.1](../GhostTool_User_Manual.md). Os nomes dos controles em inglês são mantidos para localizar os botões no Bforartists. Esta tradução não passou por revisão linguística profissional.

O Ghost Tool para Bforartists exibe malhas fantasma, trajetórias e marcadores de movimento editáveis. O manual da versão 4.3.1 inclui a barra direta da vista, contagens Before/Ahead separadas, ajustes ao manter pressionado, arraste persistente de marcadores e restauração atualizada dos marcadores de instantâneos.

Este manual acompanha o [ZIP de instalação do Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Atualizar o repositório não atualiza automaticamente o complemento instalado: instale o novo ZIP e reinicie o Bforartists. Consulte as [notas da versão](../releases/4.3.1/RELEASE-NOTES.md) e o [registro do pacote](../releases/4.3.1/package-receipt.json) para conferir versão e soma de verificação.

## Instalar e encontrar o Ghost Tool

Baixe `b4_ghost_tool_v4.3.1.zip` e instale por Edit > Preferences > Add-ons > Install from Disk. Ative o Ghost Tool e reinicie o Bforartists após substituir a versão instalada. Confira se Preferences informa 4.3.1. Um ZIP antigo continua instalando sua versão original.

Por padrão, o Ghost Tool usa Top Toolbar, na linha nativa Tool Settings da vista 3D. Com os cabeçalhos no topo, essa linha fica logo abaixo do cabeçalho principal e acompanha seu alinhamento. Preferences também oferece Right Sidebar (N) e Left Tool Shelf (T). Escolhas antigas de Top Header migram para a barra visível; a preferência agora se chama Top Toolbar.

Os controles nativos de ferramenta e modo continuam disponíveis. Vistas estreitas ou divididas mantêm a barra Ghost completa na mesma ordem. Arraste a linha horizontalmente com o botão central do mouse para alcançar controles fora da área visível. Se estiverem ocultos, escolha View > Show Ghost Toolbar. Salve as preferências normalmente para preservar sua escolha de exibição.

## Início rápido: examinar um alvo animado

Selecione um objeto animado ou osso de pose e ative o primeiro ícone de fantasma. Clique em Ghosts para mostrar as prévias das malhas; ajuste Before e Ahead separadamente. Escolha Wire ou Solid para a aparência. Mantenha Ghosts pressionado para escolher amostragem por passos de quadros ou quadros-chave e ajustar opacidade, desvanecimento ou In Front.

Clique em Paths para mostrar uma trajetória. Se não houver alvo de trajetória, a ação pode adicionar o alvo animado selecionado. Use Add Selected Path para outro alvo ou Follow Selection para acompanhar a seleção atual. Ative Markers Display para revelar pontos editáveis de uma trajetória adicionada à lista.

Clique em Drag e depois selecione e mova marcadores na vista 3D. Confirme um movimento e escolha outro marcador sem reiniciar Drag. Clique novamente em Drag ou pressione Escape para sair. Antes de editar, mantenha Drag pressionado para escolher como soltar um marcador afeta a animação.

## Ler a barra superior da esquerda para a direita

**Ghost Tool:** o primeiro ícone ativa ou desativa a ferramenta inteira. É independente do botão Ghosts de exibição das malhas. Desativá-lo também desarma os modos de edição de marcadores e alças. Mantenha-o pressionado para Update Meshes While Scrubbing, Update Markers While Scrubbing e Freeze Updates.

**Ghosts:** clique para mostrar ou ocultar as malhas fantasma. Os números Before e Ahead têm seus próprios botões menos e mais. Wire Ghosts e Solid Ghosts selecionam o estilo explicitamente. Ocultar as malhas preserva o estilo; escolher um estilo não funciona como interruptor de visibilidade.

**Paths:** mostra ou oculta trajetórias. Suas próprias contagens Before e Ahead são seguidas de Add Selected Path e Follow Selection. Alvos adicionados permanecem ao selecionar outro objeto ou osso. Follow Selection acrescenta uma prévia da seleção atual. Alvos de trajetória e marcadores fixados para edição são conceitos diferentes.

**Drag:** inicia o modo persistente Drag Markers. **Pin:** inicia a escolha de um marcador para fixá-lo ou liberá-lo. **Markers Display:** o botão em losango imediatamente à direita de Pin mostra ou oculta marcadores editáveis nas trajetórias. As dicas ao passar o mouse identificam cada ferramenta.

**Arc Style:** um clique abre diretamente Solid, Speed Colored e Fade. Controla o arco de movimento Ghost, não os estilos Wire ou Solid das malhas. Paths tem um Line Style separado no menu de pressão prolongada. **Spacing Ticks:** alterna os indicadores de espaçamento; mantenha pressionado para Acceleration Indicators.

**Settings:** abre os controles avançados de geração de marcadores, alvos, intervalo, edição, comparação, física e aparência. Generate e Clear não são mais repetidos como ícones independentes na linha superior. Essas operações continuam nos controles avançados.

## Ajustar as contagens Before e Ahead

Há dois números junto a Ghosts e outros dois junto a Paths. O primeiro, Before, conta amostras anteriores ao quadro atual. O segundo, Ahead, conta amostras posteriores. São contagens independentes, não um único controle de densidade. Edite diretamente um número ou use seus botões menos e mais na barra superior. Zero desativa as amostras daquele lado.

As contagens determinam quantas amostras solicitar; a amostragem determina onde ficam. Com o cursor temporal no quadro 20, Ghosts Before 3, Ahead 2 e passo 2 solicitam amostras em 18, 16 e 14 antes, e 22 e 24 depois, conforme os limites de intervalo e a animação disponível. A pose do quadro atual não entra nessas contagens anteriores/posteriores.

By Keyframe usa as chaves de animação do alvo em vez de quadros igualmente espaçados. Seu intervalo pode pular chaves. Editar as contagens de Paths seleciona a janela baseada em quantidade ao redor do cursor temporal. Modos avançados de intervalo de quadros continuam em Settings e seguem suas próprias regras.

## Manter uma ferramenta pressionada para seus ajustes

Um clique normal executa a ação principal. Mantenha pressionado um botão compatível para abrir os parâmetros. Arc Style é a exceção: um clique abre imediatamente suas três opções. Settings também abre o painel avançado com um clique normal.

**Manter Ghosts:** escolha amostragem por passos ou por chaves. O primeiro modo mostra Every (Frames); 1 usa cada quadro. O segundo mostra Keyframe Interval, incluindo intervalo personalizado. As opções de aparência incluem Opacity, In Front e Fade.

**Manter Paths:** escolha a amostragem e seu intervalo em quadros ou chaves. Line Style, Frame Numbers e Bezier Handles controlam a exibição. Ative Bezier Handles para examinar ou editar as alças das curvas.

**Manter Markers Display:** altere a amostragem compartilhada com Motion Paths, os pontos de quadros-chave e os números dos marcadores. Esse menu está na barra superior. Os marcadores não têm um terceiro modo independente: alterar aqui também muda a amostragem de Paths.

**Manter Drag:** escolha When Released, Curve Shape ou Smooth Neighbours conforme o modo, Nearby Frame Reach e Falloff. **Manter Pin:** leia as instruções ou escolha Unpin All Markers. **Manter Follow Selection:** ajuste Highlight Active Path. **Manter Spacing Ticks:** escolha Acceleration Indicators.

## Usar a barra inferior da Timeline

A faixa Ghost compacta fica na mesma linha dos botões nativos da Timeline. Não é uma segunda linha personalizada abaixo da barra da Timeline. A atualização documental 4.3.1 não redesenha essa faixa.

A ordem é: ativação geral; exibição de malhas Ghosts; contagens anteriores/posteriores das malhas; Wire e Solid; Drag Markers; losango de marcadores editáveis; Paths; contagens anteriores/posteriores da trajetória. Cada par segue a mesma ordem antes/depois da barra superior.

Mantenha Ghosts ou Paths na Timeline para Frame by Frame, By Keyframe, intervalos e ajustes visuais. More Ghost Settings abre as opções completas. O losango inferior é um interruptor direto; seu menu separado fica em Markers Display na barra superior. Instantâneos ficam em Compare nos ajustes avançados, não como botão da faixa inferior.

## Arrastar vários marcadores em sequência

Ative o Ghost Tool e mostre marcadores editáveis de um alvo animado. Drag arma o seletor; o texto de estado solicita um marcador na vista 3D. Clicar no vazio mantém o seletor aguardando: aproxime-se de um marcador visível. Confirmar um movimento deixa Drag ativo para a próxima edição. Todos os botões Drag Markers compartilham esse modo.

Clique novamente em Drag ou pressione Escape para desligá-lo. Escape durante um movimento cancela esse movimento e restaura suas curvas e posições iniciais. Movimentos já confirmados são edições separadas; reverta-os com Undo. Desativar a ferramenta, perder um alvo, mudar de arquivo/histórico ou desligar o complemento também encerra ou cancela as sessões afetadas.

O arraste das alças de trajetória também oferece espera persistente. Mostre Bezier Handles, inicie sua ação de arraste e escolha alças visíveis sucessivamente. Shift+G continua disponível. Alt alterna o alinhamento das alças durante o arraste. Escape cancela o movimento de alça em andamento e sai do modo.

## Escolher movimentos suaves ou angulosos

Mantenha Drag e examine When Released. Reshape Handles altera alças Bézier existentes para a curva passar pela amostra movida sem adicionar uma chave. Curve Shape oferece Free, Locked e Smooth: Free permite ajuste livre; Locked preserva os ângulos; Smooth redistribui a influência das alças pelo segmento.

Insert Keyframe grava uma chave real no quadro do marcador. Smooth Neighbours pode suavizar as alças das chaves vizinhas após essa inserção. Nearby Frame Reach e Falloff controlam a participação dos quadros próximos na escultura do movimento.

A linha visível também depende da densidade de amostragem. Amostras muito espaçadas produzem uma linha grosseira mesmo que a animação seja curva. Use um passo menor para examinar o resultado. Uma mudança brusca pode vir da interpolação, das alças ou do modo de edição; aumentar apenas as amostras visuais não muda a forma da curva animada.

## Fixar marcadores e gerenciar alvos de trajetória

Clique em Pin e depois em um marcador visível para alternar sua fixação. Pin é uma escolha pontual, não o modo persistente Drag; execute-o novamente para outro marcador. É possível fixar vários, não apenas um. Os marcadores ficam imóveis durante a remodelagem, e uma atualização preserva os registros fixados correspondentes. Mantenha Pin e escolha Unpin All Markers para liberar todos.

Adicionar um alvo de trajetória mantém o objeto ou osso na lista; não congela todas as suas amostras de animação. Follow Selection muda a prévia da seleção enquanto os alvos adicionados explicitamente permanecem. Gerencie-os na lista de Paths em Settings. Use Markers Display para os pontos editáveis dessas trajetórias; Keyframe Dots é uma ajuda visual separada.

## Atualizações ao vivo e edição nativa

Live Update Markers e Live Update Skin vêm desligados; cenas existentes preservam seus valores salvos. Desligados, percorrer a Timeline mantém a última prévia atualizada. Mude isso nas opções sob o ícone principal Ghost. Freeze Updates também pausa os refrescos automáticos.

Durante movimentos, rotações, escalas e gestos nativos com gizmos, Ghost preserva a prévia em vez de percorrer quadros. Depois de confirmar ou cancelar, espera as edições estabilizarem e atualiza os fantasmas existentes. Auto-key pode continuar ativo; sem ele, insira a chave desejada após confirmar a pose. Generate nos controles avançados regenera os marcadores explicitamente quando necessário.

Os controles avançados mantêm Marker Targets, fontes de onion skin, intervalo, subdivisão e aparência. A visibilidade de marcadores e peles em cache mostra ou oculta as prévias existentes sem reconstruí-las. Clear All Ghosts remove marcadores e onion skins; use visibilidade quando quiser apenas ocultar. Marcadores ocultos não podem ser clicados nem selecionados por caixa.

## Salvar, comparar e restaurar instantâneos

Abra Compare por Settings. Antes de Save Snapshot, escolha o escopo: Active Object / Selected Bones, Selected Path, canais dos marcadores selecionados ou escopo explícito de cena. Confira o alvo mostrado. Instantâneos guardam amostras congeladas e chaves/alças capturadas. Ficam na cena e sobrevivem à reabertura e à desativação/reativação do complemento.

Hide/Show muda a sobreposição de um instantâneo sem alterar a animação. Save Variant cria uma alternativa independente com a origem registrada; excluir o pai preserva a variante. Ao chegar a dez instantâneos, exclua os desnecessários antes de salvar outro. Captura, variantes, vinculação, visibilidade, exclusão e restauração participam do Undo/Redo nativo.

Restore valida identidade de cena, objeto, ação, slot, osso e canal antes de gravar. Restaura curvas e registros de marcadores do escopo capturado e atualiza a exibição, mesmo com atualizações ao vivo desligadas ou congeladas. Não restaura objetos alheios nem modificadores arbitrários de Action. Referências antigas só de amostras restauram valores adequados onde a curva pode ser remodelada.

Alvos substituídos exigem vinculação deliberada. Slots de ação compartilhados são recusados: torne a animação de usuário único primeiro. Bind to Active Target aceita um objeto original e seus canais de ossos nomeados por referência. Referências importadas com vários objetos continuam visíveis e sem vínculo, sem serem reduzidas a um alvo. Renomeações de ossos são acompanhadas. Após reabrir, a identidade do canal identifica a curva; durante um gesto, uma curva substituída não recebe a reversão destinada à original.

## Transferir instantâneos e usar ferramentas avançadas

Exporte instantâneos em JSON para transferir dados de comparação. A importação valida e mescla registros, remapeia IDs em conflito e rejeita atomicamente versões incompatíveis ou excesso de capacidade. Referências importadas e antigas continuam visíveis, mas a restauração exige vínculo explícito porque JSON não comprova a identidade do objeto original. Uma importação que falha preserva os registros existentes ilegíveis da cena.

Edit Motion mantém predefinições e controles personalizados de easing. Draw to Keys converte o maior traço de anotação em trajetória de posição; traços transversais identificam as chaves. O diálogo preserva o alvo selecionado. Physics Feel, Look, Compare e outros recursos avançados continuam acessíveis por Settings e pelas localizações alternativas de painel lateral ou estante.

## Solução de problemas e notas de versão

Se nada aparecer, confira o primeiro ícone Ghost, se o alvo é animado, se a exibição correspondente está ativa e se suas contagens são maiores que zero. Se faltarem pontos editáveis, adicione o alvo a Paths e ative Markers Display. Mais amostras visíveis podem exigir passo menor ou outro intervalo de chaves. A amostragem dos marcadores acompanha Paths.

Se a barra desaparecer, escolha Top Toolbar nas preferências Ghost e View > Show Ghost Toolbar. Se ficar cortada numa vista dividida, role a linha horizontalmente. Preferências de largura da estante esquerda continuam disponíveis; sua verificação completa de largura/escala estava incompleta em 4.2.11. Esta versão não promete corrigir todos esses casos.

A implementação direta recebeu 188 verificações específicas em segundo plano antes desta atualização de versão/documentação, cobrindo interface, edição, trajetórias, instantâneos, início, localização e cache. Os resultados são da implementação já verificada. O arquivo 4.3.1 também teve integridade ZIP, versão e correspondência exata com o código-fonte conferidas; esta etapa de empacotamento não afirma uma nova execução de testes funcionais. Informe alvo, operação e etapa com falha no [rastreador de problemas](https://github.com/Axleonex/B4Artists_Toolkit/issues).
