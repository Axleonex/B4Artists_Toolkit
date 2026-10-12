# O pipeline do CATS

[← Sumário](index.md)

**Leia isto antes de usar qualquer ferramenta do CATS pela primeira vez.**

As ferramentas do CATS não são um menu de opções independentes: elas formam um pipeline. Cada passo se apoia no anterior. Executá-las fora de ordem produz resultados quebrados que ficam invisíveis até você já estar no VRChat, e aí não dá para consertar sem começar de novo. Você pode pular uma fase de que seu avatar não precisa, mas as fases que você executa têm de manter esta ordem.

---

## As seis fases, em ordem

O Status do Pipeline da aba CATS lista as fases e marca cada uma quando ela termina:

1. **Corrigir Modelo** — Limpa a malha: remove duplicados e geometria quebrada, corrige as normais. Todos os outros passos dependem deste.

2. **Atlas de Materiais** — Combina os materiais do avatar em uma só folha de textura (opcional, para o desempenho).

3. **Visemas** — Gera as 15 formas de boca de sincronia labial do VRChat a partir das suas três formas base (A, O, CH).

4. **Rastreamento Ocular** — Configura o movimento dos olhos do VRChat com os ossos dos olhos do seu avatar.

5. **Pose para Shape Key** — Captura poses ou expressões personalizadas como shape keys.

6. **Aplicar Todos os Transformes** — Congela toda a posição, rotação e escala para que seu avatar tenha transformações limpas no envio.

---

## Status do Pipeline e Registro de Operações

O Status do Pipeline mostra uma linha por fase. Quando uma fase termina, a linha dela mostra uma marca. O status fica salvo na cena, então permanece com o seu arquivo.

O Registro de Operações lista cada operação do CATS que você executou, a mais recente por último, com a hora e o resultado: Changed (mudou o modelo), Clean (nada precisou mudar) ou Failed (falhou). **Copiar** coloca o registro na área de transferência (útil quando você pede ajuda); **Limpar** o esvazia.

A ordem é um conselho, não uma trava: uma ferramenta cuja fase anterior não foi feita roda mesmo assim, mas mostra um aviso como "Run Fix Model first for best results" (execute primeiro Corrigir Modelo para obter os melhores resultados). Leve esse aviso a sério.

---

## Por que esta ordem

Cada fase muda a malha ou o esqueleto de um jeito do qual a próxima depende:

- **Corrigir Modelo tem de vir primeiro** porque muda o número de vértices, remove duplicados e corrige as normais. Qualquer ferramenta que lê posições de vértices (geração de visemas, detecção de ossos dos olhos, captura de poses) dá resultados errados em uma malha que ainda tem vértices duplicados ou quebrados.

- **Visemas antes de Rastreamento Ocular** porque os dois mudam shape keys e dados de ossos. Nesta ordem, os shape keys existem antes de as restrições serem escritas.

- **Rastreamento Ocular antes de Pose para Shape Key** porque Pose para Shape Key captura a malha inteira, inclusive a deformação causada pelos ossos. Com as restrições dos olhos já no lugar, a posição neutra dos olhos na forma salva fica correta.

- **Aplicar transformações por último** porque isso congela tudo de vez. Qualquer geometria não corrigida, shape key não mapeado ou restrição errada fica travada. Depois de aplicar as transformações, os únicos jeitos de voltar a uma fase anterior são desfazer (Ctrl+Z) ou reimportar do arquivo de origem.

---

## O que quebra se você pular um passo

**Pular Corrigir Modelo:**
Cada ferramenta seguinte trabalha em uma malha que pode ter vértices duplicados na mesma posição. Um visema gerado pode então mover o vértice visível, mas não o duplicado oculto, e no VRChat os dois se separam e rasgam a boca a cada forma de sincronia labial. O rastreamento ocular pode prender suas restrições à malha de olho duplicada em vez da visível, travando os olhos em um olhar fixo. Aplicar transformações depois grava todos esses erros.

**Pular Visemas:**
Sem visemas gerados ou mapeados, seu avatar não tem sincronia labial. Se seu avatar já tem shape keys de visemas, mapeie-os no VRChat Viseme Mapping (guia 8) em vez de gerar novos; o Status do Pipeline deixa então Visemas desmarcado, e tudo bem.

**Pular Rastreamento Ocular:**
Seu avatar não mexe os olhos no VRChat e fica olhando fixo para a frente. Isso é aceitável quando ele não tem ossos dos olhos.

**Pular Pose para Shape Key:**
Opcional: pule se você não tiver expressões personalizadas para salvar.

Próximo: [Ferramentas de rig](05-rig-tools.md)
