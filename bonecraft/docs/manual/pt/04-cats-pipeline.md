# O pipeline do CATS

[← Conteúdo](index.md)

**Leia isto antes de usar qualquer ferramenta CATS pela primeira vez.**

As ferramentas CATS não são um menu de opções independentes – elas são um pipeline. Cada etapa se baseia na anterior. Executá-los fora de ordem produz resultados quebrados que permanecem invisíveis até que você já esteja em VRChat e, a essa altura, eles não podem ser corrigidos sem começar de novo. Você pode pular uma fase que seu avatar não precisa, mas as fases que você executa devem manter esta ordem.

---

## As seis fases, em ordem

O status do pipeline da guia CATS lista as fases e marca cada uma delas quando termina:

1. **Fix Model** — Limpe a malha: remova duplicatas e geometria quebrada, corrija normais. Todas as outras etapas dependem desta.

2. **Material Atlas** — Combine os materiais do avatar em uma folha de textura (opcional, para desempenho).

3. **Visemes** – Gere os 15 formatos de boca com sincronização labial VRChat a partir de seus três formatos básicos (A, O, CH).

4. **Eye Tracking** — Configure o movimento dos olhos de VRChat com os ossos oculares do seu avatar.

5. **Pose to Shape Key** — Capture poses ou expressões personalizadas como chaves de forma.

6. **Apply All Transforms** — Congele todas as posições, rotações e escalas para que seu avatar tenha transformações limpas para upload.

---

## Status do Pipeline e Registro de Operações

O status do pipeline mostra uma linha por fase. Quando uma fase termina, sua linha mostra uma marca de seleção. O status é mantido na cena, portanto permanece no seu arquivo.

O livro-razão de operações lista cada operação CATS que você executou, a mais recente por último, com seu tempo e resultado: Alterado (mudou o modelo), Limpo (nada precisava ser alterado) ou Com falha. **Copy** coloca o livro-razão na área de transferência (útil quando você pede ajuda);**Clear** o esvazia.

A ordem é um conselho, não um bloqueio: uma ferramenta cuja fase anterior não foi concluída ainda é executada, mas mostra um aviso como "Execute o modelo de correção primeiro para obter melhores resultados". Leve o aviso a sério.

---

## Por que esta ordem

Cada fase altera a malha ou esqueleto de uma forma que a próxima depende:

- **Fix Model deve ser o primeiro** porque altera a contagem de vértices, remove duplicatas e corrige normais. Qualquer ferramenta que leia posições de vértices (geração de visema, detecção de osso ocular, captura de pose) produz resultados errados em uma malha que ainda possui vértices duplicados ou quebrados.

- **Visemas antes do rastreamento ocular** porque ambos alteram a chave de forma e os dados ósseos. Nesta ordem, as chaves de forma existem antes das restrições serem escritas.

- **Rastreamento ocular antes do Pose to Shape** porque o Pose to Shape captura toda a malha, incluindo a deformação causada pelos ossos. Com as restrições do olho instaladas primeiro, a posição neutra do olho na forma salva estará correta.

- **Aplique Transforms por último** porque congela tudo para sempre. Qualquer geometria não fixa, chaves de forma não mapeadas ou restrições erradas são bloqueadas. Depois de aplicar as transformações, as únicas maneiras de voltar a uma fase anterior são desfazer (Ctrl+Z) ou reimportar do arquivo de origem.

---

## O que quebra se você pular um passo

**Ignorar modelo de correção:**
Cada ferramenta posterior funciona em uma malha que pode conter vértices duplicados na mesma posição. Um visema gerado pode então mover o vértice visível, mas não sua duplicata oculta, então em VRChat os dois se separam e rasgam a boca em cada formato de sincronização labial. O rastreamento ocular pode anexar suas restrições à malha ocular duplicada em vez da malha visível, prendendo os olhos em um olhar fixo. Apply Transforms então incorpora todos esses erros.

**Pular Visemas:**
Sem visemas gerados ou mapeados seu avatar não tem sincronização labial. Se o seu avatar já possui chaves de forma de visema, mapeie-as em VRChat Mapeamento de Visema (Guia 8) em vez de gerar novas; O status do pipeline mostra Visemes desmarcados, o que é bom.

**Pular rastreamento ocular:**
Seu avatar não tem movimento ocular em VRChat e olha para frente. Isso é aceitável quando não possui ossos oculares.

**Pular pose para moldar:**
Opcional: ignore-o se não tiver expressões personalizadas para salvar.

Próximo: [Ferramentas de plataforma](05-rig-tools.md)
