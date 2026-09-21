# Projected-risk selector v26: unqualified

The primary run completed 7,358 training windows, projected costs for 12 whole-interval choices, and a prospectively fixed 596-input/32-hidden selector trained for 60 epochs. Weights froze before development data was loaded. Model SHA-256: `310fa08151708ab8e1d076dc370b8b40fb0c6a7680e078c7389d6c8fee895bb3`.

| Development partition | Average position improvement | Worst cohort ratio | Qualified |
|---|---:|---:|---|
| Old, 480 windows | 5.16% | 2.90167 | No |
| New, 288 windows | 7.39% | 1.10217 | No |
| Combined, 768 windows | 6.59% | 2.90167 | No |

All original aggregate rotation, velocity, acceleration and segment-length checks pass. Priority positions/rotations and physical-edge bounds pass. Every partition fails the unchanged 1.10 worst-cohort requirement. These metrics do not establish visual quality or Cascadeur parity. All three matched procedural controls reproduce their earlier development results exactly. Learned-expert components were selected for 331 of 768 windows; other selected proposals remain procedural.

## Failures

Three of 96 exposed groups fail: `28_01/gap32/context1` (2.90167), `13_12/gap32/context1` (1.37466), and `141_09/gap32/context0` (1.10217). Compared with v23, six failures clear and two new failures appear; 54 groups improve and 42 worsen. The old worst failure becomes substantially worse. Fewer failed groups does not make this candidate qualified.

The predeclared edit diagnostic covers 96 existing representative windows, three axes, both signs, and three endpoint-translation sizes: 1,728 cases. At 1e-5 and 1e-4 body-reference units no candidate switches occurred. At 1e-3, 13 of 576 probes switched. The largest isolated selection jump was 1.624 body-reference units or 2.997 radians. These are raw-proposal measurements, before physical projection or rig fitting; no claim about displayed motion is made. They demonstrate that hard whole-interval choice can be discontinuous under small edits.

## Native checks and next action

Sixteen moving-rig and sixteen stationary-rig cases pass with source/priority recovery. Fifteen action/recovery methods pass; 11 actually invoke the trained provider, making 28 provider calls. These establish bounded pipeline behavior, not motion qualification. The additional 25-method cooperative/lifecycle check also passes; 20 methods invoke the trained provider, making 74 calls. Together these are 72 native case/method executions through distinct paths, not independent motion-quality assessments. The reproduction run produced byte-identical frozen weights; its development evaluation and complete artifact comparison remain pending. The host still exits with its separately reproduced shutdown access violation after successful assertions.

Keep the v26 weights, protocol, data and failed results unchanged. Confirmation remains sealed; no temporal weights are bundled or promoted. Complete reproducibility and cooperative validation, then investigate a prospectively fixed continuous proposal mechanism using training evidence. Any replacement must pass the original development gates and separate edit-stability and animator checks. The full original goal, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain unchanged.

The current shared goal evaluator requires host-authenticated assessment envelopes that are unavailable here. Formal checks therefore remain unknown under that policy; raw tests, benchmark artifacts, historical accepted evidence and regression floors remain preserved.
