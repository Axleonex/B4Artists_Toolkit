# Ghost Tool 4.3.1 - Guia do usuário

Tradução automática da edição inglesa 4.3.1, sem certificação profissional. Os nomes dos controles permanecem em inglês para corresponder à interface. [Fonte em inglês](../../GhostTool_User_Manual.md).

O Ghost Tool para Bforartists exibe malhas fantasma, trajetórias de movimento e marcadores editáveis. A versão 4.3.1 inclui neste guia a barra direta da vista 3D, contagens Before/Ahead separadas, configurações por pressionamento prolongado, arraste contínuo de marcadores e restauração atualizada dos marcadores de snapshots.

Este guia acompanha o [ZIP de instalação do Ghost Tool 4.3.1](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/ghost-v4.3.1/b4_ghost_tool_v4.3.1.zip). Atualizar o código do repositório não atualiza automaticamente a extensão instalada: instale o novo ZIP e reinicie o Bforartists. Consulte as [notas da versão](../../releases/4.3.1/RELEASE-NOTES.md) e o [registro do pacote](../../releases/4.3.1/package-receipt.json) para verificar a versão e a soma de verificação.

## Instalar e encontrar o Ghost Tool

Baixe `b4_ghost_tool_v4.3.1.zip` e instale por Edit > Preferences > Add-ons > Install from Disk. Ative o Ghost Tool e reinicie o Bforartists após substituir uma versão instalada. Confira se Preferences mostra 4.3.1. Um ZIP antigo continua instalando sua versão original.

Por padrão, o Ghost Tool usa Top Toolbar na linha nativa Tool Settings da vista 3D. Com os cabeçalhos nativos no topo, essa linha fica logo abaixo do cabeçalho principal e acompanha seu alinhamento. As preferências também oferecem Right Sidebar (N) e Left Tool Shelf (T). A antiga escolha salva Top Header migra para a barra visível; a preferência agora se chama Top Toolbar.

Os controles nativos de ferramenta e modo continuam disponíveis. Vistas estreitas ou divididas mantêm todas as ferramentas Ghost na mesma ordem; arraste a linha horizontalmente com o botão do meio do mouse para alcançar controles fora da área visível. Se estiverem ocultos, use View > Show Ghost Toolbar. Salve as preferências normalmente para manter suas escolhas de exibição.

## Início rápido: inspecionar um alvo animado

Selecione um objeto animado ou osso em modo Pose e ative o primeiro ícone de fantasma. Clique em Ghosts para mostrar as prévias de malha; ajuste Before e Ahead separadamente. Clique em Wire ou Solid para escolher a aparência. Mantenha Ghosts pressionado para escolher amostragem por intervalo de quadros ou por quadros-chave e ajustar Opacity, Fade ou In Front.

Clique em Paths para exibir uma trajetória. Se ainda não houver alvo de trajetória, a ação pode adicionar o alvo animado selecionado. Use Add Selected Path para outro alvo ou Follow Selection para acompanhar a seleção atual. Ative Markers Display para mostrar os pontos editáveis de uma trajetória mantida na lista.

Clique em Drag, escolha e mova marcadores na vista 3D. Confirme um movimento e escolha outro marcador sem reiniciar Drag. Clique novamente em Drag ou pressione Escape para sair. Antes de editar, mantenha Drag pressionado para escolher como a soltura afeta a animação.

## Ler a barra superior da esquerda para a direita

**Ghost Tool:** o primeiro ícone ativa ou desativa a ferramenta inteira, independentemente do botão de exibição de malhas Ghosts. Desativá-la também encerra os modos de edição de marcadores e alças. Mantenha pressionado para Update Meshes While Scrubbing, Update Markers While Scrubbing e Freeze Updates.

**Ghosts:** mostra ou oculta malhas fantasma. Os campos Before e Ahead ao lado têm botões de menos e mais próprios. Wire Ghosts e Solid Ghosts selecionam explicitamente o estilo. Ocultar as malhas preserva o estilo; selecionar um estilo não funciona como interruptor de visibilidade.

**Paths:** mostra ou oculta trajetórias. Seus campos Before e Ahead são seguidos por Add Selected Path e Follow Selection. Alvos adicionados permanecem ao selecionar outro objeto ou osso. Follow Selection acrescenta uma prévia da seleção atual. Alvos de trajetória e marcadores de edição fixados são conceitos diferentes.

**Drag:** inicia o modo contínuo Drag Markers. **Pin:** inicia a escolha de um marcador para fixar ou desafixar. **Markers Display:** o losango imediatamente à direita de Pin mostra ou oculta marcadores editáveis da trajetória. As dicas ao passar o mouse identificam cada ferramenta.

**Arc Style:** abre com um clique as opções Solid, Speed Colored e Fade. Controla o arco de movimento dos fantasmas, não a exibição Wire/Solid das malhas. Paths possui Line Style separado no menu por pressionamento prolongado. **Spacing Ticks:** alterna indicadores de espaçamento; mantenha pressionado para Acceleration Indicators.

**Settings:** abre controles avançados de geração de marcadores, alvos, intervalos, edição, comparação, física e aparência. Generate e Clear não se repetem mais como ícones isolados na barra superior; continuam nos controles avançados.

## Ajustar as contagens Before e Ahead

Há dois números ao lado de Ghosts e dois ao lado de Paths. O primeiro, Before, solicita amostras anteriores ao quadro atual. O segundo, Ahead, solicita amostras posteriores. São contagens independentes, não uma densidade combinada. Edite diretamente ou use menos/mais na barra superior. Zero desativa amostras daquele lado.

As contagens definem quantas amostras solicitar; a amostragem define onde ficam. No quadro 20, Ghosts Before 3, Ahead 2 e intervalo de 2 solicitam amostras anteriores em 18, 16 e 14 e posteriores em 22 e 24, respeitando a animação disponível e os limites do intervalo. A pose no indicador de reprodução não entra nessas amostras.

By Keyframe usa as chaves de animação do alvo em vez de quadros igualmente espaçados. Seu intervalo pode pular chaves. Editar os campos de contagem de Paths seleciona a janela baseada em contagens ao redor do quadro atual. Modos avançados de intervalo de quadros continuam em Settings e seguem suas próprias regras.

## Manter uma ferramenta pressionada para configurar

Um clique normal executa a ação principal. Manter um botão compatível pressionado abre seus parâmetros. Arc Style é a exceção: um clique abre imediatamente as três opções. Settings abre o painel avançado com clique normal.

**Manter Ghosts pressionado:** escolhe amostragem por intervalo de quadros ou quadros-chave. A primeira mostra Every (Frames); 1 significa todos os quadros. A segunda mostra Keyframe Interval, inclusive intervalo personalizado. Opacity, In Front e Fade ajustam a aparência.

**Manter Paths pressionado:** escolhe a amostragem e o intervalo de quadros ou chaves. Line Style, Frame Numbers e Bezier Handles controlam a exibição. Ative Bezier Handles para inspecionar ou editar alças das curvas.

**Manter Markers Display pressionado:** altera a amostragem compartilhada com Motion Paths, mostra pontos dos quadros-chave e alterna números dos quadros dos marcadores. Esse menu fica na barra superior. Marcadores não têm um terceiro modo independente: mudar aqui também altera a amostragem de Paths.

**Manter Drag pressionado:** configura When Released, Curve Shape ou Smooth Neighbours conforme o modo, Nearby Frame Reach e Falloff. **Pin:** mostra instruções ou Unpin All Markers. **Follow Selection:** ajusta Highlight Active Path. **Spacing Ticks:** oferece Acceleration Indicators.

## Usar a barra inferior da Timeline

A faixa compacta Ghost fica na mesma linha dos botões nativos da Timeline. Não há uma segunda linha personalizada abaixo. A atualização documental 4.3.1 não redesenha essa faixa.

A ordem é: ativação geral; exibição de malhas Ghosts; contagens de malhas anteriores e posteriores; Wire e Solid; Drag Markers; losango dos marcadores editáveis; exibição Paths; contagens de trajetória anteriores e posteriores. Cada par segue a mesma ordem antes/depois da barra superior.

Mantenha Ghosts ou Paths da Timeline pressionado para Frame by Frame, By Keyframe, intervalos de amostragem e exibição. More Ghost Settings abre as opções completas. O losango inferior alterna diretamente os marcadores; seu menu separado por pressionamento prolongado fica em Markers Display na barra superior. Snapshots ficam em Compare nos ajustes avançados, não em um botão inferior.

## Arrastar marcadores repetidamente

Ative o Ghost Tool e mostre os marcadores editáveis de um alvo animado. Drag prepara a seleção; o texto de estado pede um clique em um marcador na vista 3D. Clicar no espaço vazio mantém a espera: aproxime-se de um marcador visível. Confirmar um movimento mantém Drag ativo para a próxima edição. Todos os botões que iniciam Drag Markers compartilham esse modo.

Clique novamente em Drag ou pressione Escape para desligar. Durante um movimento, Escape cancela esse movimento e restaura as curvas e posições originais. Movimentos anteriores confirmados são edições separadas; use Undo para revertê-los. Desativar a ferramenta, perder um alvo, mudar de arquivo/histórico ou encerrar a extensão também termina ou cancela as sessões afetadas.

Arrastar alças de trajetória também permite espera contínua. Mostre Bezier Handles, inicie o arraste de alças e escolha alças visíveis sucessivamente. Shift+G continua disponível. Alt alterna o comportamento de alças alinhadas durante o arraste. Escape cancela o movimento em andamento e sai do modo.

## Escolher edições suaves ou angulares

Mantenha Drag pressionado e consulte When Released. Reshape Handles modifica alças de Bézier existentes para passar a curva pela amostra movida sem adicionar quadro-chave. Curve Shape oferece Free, Locked e Smooth: Free permite ajustes livres; Locked preserva os ângulos; Smooth redistribui a influência das alças ao longo do segmento.

Insert Keyframe grava uma chave real no quadro do marcador. Smooth Neighbours pode suavizar as alças das chaves adjacentes após a inserção. Nearby Frame Reach e Falloff controlam a participação dos quadros próximos na escultura.

A linha visível também depende da densidade das amostras. Amostras muito espaçadas formam uma linha grosseira mesmo quando a animação subjacente é curva. Use um intervalo menor para examinar o resultado. Uma mudança brusca pode vir da interpolação, das alças ou do modo de edição; adicionar apenas amostras de exibição não muda a curva da animação.

## Fixar marcadores e gerenciar alvos de trajetória

Clique em Pin e depois em um marcador visível para alternar sua fixação. Pin faz uma escolha única, não o arraste contínuo de Drag; acione novamente para outro marcador. É possível fixar vários marcadores. Eles ficam imóveis durante a remodelagem, e uma atualização preserva registros fixados correspondentes. Mantenha Pin pressionado e escolha Unpin All Markers para liberar todos.

Adicionar um alvo mantém o objeto ou osso na lista de trajetórias; não congela todas as amostras de sua animação. Follow Selection muda a prévia da seleção enquanto alvos explicitamente adicionados permanecem. Gerencie-os na lista de Settings. Use Markers Display para pontos editáveis nas trajetórias mantidas; Keyframe Dots é um auxílio visual separado.

## Atualizações ao vivo e edição nativa

Live Update Markers e Live Update Skin vêm desativados; cenas existentes preservam seus valores salvos. Desativados, percorrer quadros mantém a última prévia atualizada. Use as opções sob o ícone principal para alterar isso. Freeze Updates também pausa atualizações automáticas.

Durante movimentos, rotações, escalas e gestos de gizmo nativos, Ghost conserva a última prévia em vez de percorrer quadros da animação. Após confirmar ou cancelar, espera as edições estabilizarem e atualiza os fantasmas existentes. Auto-key pode continuar ativo; sem ele, insira a chave pretendida após confirmar a pose. Generate nos controles avançados de marcadores regenera explicitamente quando necessário.

Os controles avançados mantêm Marker Targets, fontes de onion skin, intervalo, subdivisão e aparência. A visibilidade de marcadores e skins em cache mostra ou oculta prévias existentes sem reconstruí-las. Clear All Ghosts remove marcadores e onion skins; use visibilidade para apenas ocultar. Marcadores ocultos não podem ser escolhidos nem selecionados por caixa.

## Salvar, comparar e restaurar snapshots

Abra Compare por Settings. Antes de Save Snapshot, selecione o escopo: Active Object / Selected Bones, Selected Path, canais dos marcadores selecionados ou escopo explícito de cena. Confira o alvo mostrado. Snapshots guardam amostras congeladas e quadros-chave/alças capturados na cena, inclusive após salvar/reabrir ou desativar/reativar a extensão.

Hide/Show muda a sobreposição sem alterar a animação. Save Variant cria uma alternativa independente com sua origem registrada; excluir o pai preserva a variante. Ao atingir dez snapshots, exclua registros indesejados antes de salvar outro. Captura, variantes, vinculação, visibilidade, exclusão e restauração participam do Undo/Redo nativo.

Restore valida cena, objeto, ação, slot, osso e canal antes de escrever. Restaura curvas e registros de marcadores do escopo capturado e atualiza a exibição, mesmo com atualizações ao vivo desativadas ou congeladas. Não restaura objetos não relacionados nem modificadores Action arbitrários. Referências antigas apenas com amostras restauram valores adequados onde as curvas podem ser remodeladas.

Alvos substituídos exigem vinculação deliberada. Slots de ação compartilhados são recusados; torne a animação de usuário único primeiro. Bind to Active Target aceita um objeto original e seus canais de ossos nomeados por referência. Referências importadas com vários objetos permanecem visíveis e desvinculadas, sem serem reduzidas a um único alvo. Renomeações de ossos são acompanhadas. Após salvar/reabrir, a identidade do canal identifica a curva; durante um gesto, uma curva substituída não recebe escritas de reversão destinadas à original.

## Transferir snapshots e usar ferramentas avançadas

Exporte snapshots para JSON para transferir dados de comparação. A importação valida e mescla registros, remapeia colisões de IDs e rejeita atomicamente versões incompatíveis ou excesso de capacidade. Referências importadas e antigas continuam visíveis, mas a restauração exige vinculação explícita, pois JSON não comprova a identidade do objeto original. Uma importação malsucedida preserva registros de cena existentes ilegíveis.

Edit Motion mantém predefinições e controles personalizados de easing. Draw to Keys converte o traço de anotação mais longo em uma trajetória de posição; traços transversais identificam chaves. Seu diálogo preserva o alvo selecionado. Physics Feel, Look, Compare e outras ferramentas avançadas continuam em Settings e nos locais alternativos de barra lateral/estante.

## Solução de problemas e notas da versão

Se nada aparecer, confira a ativação do primeiro ícone, a animação do alvo, a exibição relevante e contagens maiores que zero. Para pontos editáveis ausentes, adicione o alvo a Paths e ative Markers Display. Mais amostras visíveis podem exigir um intervalo de quadros menor ou outro intervalo de chaves. A amostragem dos marcadores acompanha Paths.

Se a barra não aparecer, escolha Top Toolbar nas preferências Ghost e use View > Show Ghost Toolbar. Se estiver cortada numa vista dividida, role horizontalmente a linha nativa. As preferências de largura da estante esquerda continuam disponíveis; a verificação completa de largura/escala estava incompleta em 4.2.11. Esta versão não promete corrigir todos esses casos.

A implementação das ferramentas diretas recebeu 188 verificações direcionadas em segundo plano antes desta atualização de versão/documentação, cobrindo interface, edição, trajetórias, snapshots, inicialização, localização e exibição em cache. Esses resultados descrevem a implementação anteriormente testada. O arquivo 4.3.1 tem verificações separadas de integridade ZIP, metadados e correspondência byte a byte com o código; esta etapa de empacotamento não declara novos testes funcionais. Use o [rastreador de problemas](https://github.com/Axleonex/B4Artists_Toolkit/issues) para informar alvo, operação e etapa que falhou.
