# DonorBridge Project Plan

Oct 21, 2026 · @Vasumitra Gajbhiye

DonorBridge is feasible. We build a Python kidney-swap matcher and use it to answer one live question: should India allow 3-way swaps? A prototype already runs on a laptop and reproduces a published benchmark, so the seven weeks go into building it properly, not finding out whether it works.

## Feasibility

Yes, comfortably, for five people in seven weeks, as long as the team stays out of two traps: medical detail, and betting the headline on a gender result that may not appear.

Why we are confident:

- **The prototype already runs.** We generated 20 India-calibrated pools of 100 families each and solved every one exactly. On US blood-group settings it gave 48.5 transplants with 2-way swaps and 58.2 with 3-way swaps, close to the published 49.8 and 59.8 from Saidman et al.
- **It is fast.** Each exact solve took about one second on a laptop. The whole 320-solve experiment finished in under five minutes.
- **No patient data is needed.** Real Indian blood-group shares (10,000 donors) and published sensitisation rates drive a generator of realistic pools. The Glasgow benchmark pools and the kep\_solver library give an independent answer key.
- **The skills fit.** The hand-written parts are depth-first search, greedy choice and branch and bound, all within Python up to OOP. The lead handles the solver and oracle plumbing.
- **The question is live.** In May 2026 the Delhi High Court ruled the law does not limit swaps to two families, and NOTTO launched national swap matching in August 2026.

**Prototype run, 21 Oct 2026.** 20 India-calibrated pools of 100 families, each solved exactly. Expected transplants per pool, and the gain over allowing only 2-way swaps:

| Final tests that fail | 2-way only | Failure-aware 3-way | Count-maximising 3-way |
| --- | --- | --- | --- |
| 0% | 52.00 | 63.00 (+21.2%) | 63.00 (+21.2%) |
| 10% | 42.12 | 48.50 (+15.1%) | 47.24 (+12.2%) |
| 20% | 33.28 | 36.38 (+9.3%) | 34.33 (+3.2%) |
| 30% | 25.48 | 26.37 (+3.5%) | 23.99 (−5.8%) |
| 40% | 18.72 | 18.98 (+1.4%) | 15.94 (−14.9%) |
| 50% | 13.00 | 13.14 (+1.1%) | 9.90 (−23.8%) |

Takeaway: 3-way rings add about 21% when every final test passes, but under 4% once 3 in 10 fail.

Once about a quarter of final tests fail, a plan built to maximise the raw number of transplants does worse than staying 2-way. Scoring rings by expected transplants never does. That gap is the project's headline.

What could sink it:

- **Medical rabbit holes** such as tissue typing. Freeze the compatibility model in week 1.
- **"You just called a solver."** Lead with the hand-written branch and bound and greedy; label the ILP as the oracle that checks them.
- **Tool breakage.** kep\_solver fails with PuLP 4.x; it works with PuLP 2.9.0, which we tested.
- **All families are simulated.** Say so on the first results slide: real statistics, simulated patients.

## What we'll have at the end

By the presentation we hold a working, tested Python package, a demo that runs from one command, four results charts and a single defensible answer to the 3-way question.

| Deliverable | What it is | Rubric item it covers |
| --- | --- | --- |
| `donorbridge` Python package | Pool generator, compatibility graph, cycle finder, five solvers, failure simulator and metrics, built as classes behind one shared Solver interface | 4: choice of algorithm; visible OOP |
| Test suite | Brute force = branch and bound = ILP on small pools; our ILP matches kep\_solver on the Glasgow benchmark pools | Correctness evidence for 4 |
| CLI and demo notebook | `python -m donorbridge run`, `sweep` and `bench`; three scripted demos | 5: two normal cases and one edge case |
| Results pack | Four charts: transplants vs test-failure rate, India vs US pool mix, price of fairness by gender, runtime and optimality gap vs pool size | Research depth for the talk |
| The answer | The test-survival rate below which allowing 3-way swaps adds under 5% more transplants | The talk's closing line |
| Design file | Problem statement, assumptions register, dated flowchart and pseudocode, algorithm justification | 1, 2, 3 and 4 |
| AI usage log | `AI_LOG.md`: each prompt, what we kept, what we corrected | 6: AI usage |
| 10-minute deck | Slides plus three timed rehearsals | The presentation itself |
| Web viewer (stretch) | A Next.js page that draws the swap graph and the chosen rings | Demo impact |
| After December | Public repo and a two-page note, "What 3-way swaps are worth under India's blood-group mix" | Portfolio and resume |

Resume line it earns: built a kidney-exchange optimiser (cycle enumeration, exact matching, hand-written branch and bound, failure-aware ILP) whose answers match a published reference solver, and measured when 3-way swaps stop paying off under India's blood-group mix.

## How we'll go about it

We turn families into a graph, find every possible swap ring, choose the best set of rings with algorithms of rising power, and then stress-test that choice against last-minute failures.

1. **Model the pool.** Each family (one patient, one willing but incompatible donor) is a node. Draw an arrow from family $i$ to family $j$ when $i$'s donor can give to $j$'s patient: blood groups compatible and the tissue crossmatch negative. The generator uses India's blood-group mix and published sensitisation rates.
2. **Find candidate swaps.** A depth-first search lists every 2-family swap and every 3-family ring in the graph.
3. **Choose the swaps, climbing a ladder.** First come, first served as the naive baseline. Then greedy with local search. Then exact 2-way matching, which is fast and provably optimal. Then our own branch and bound for exact answers with 3-way rings on small pools. An ILP solver sits at the top as the oracle that checks everything at scale.
4. **Make it failure-aware.** A ring only goes ahead if every final crossmatch in it passes, so we score each ring by its expected transplants, not its size.
5. **Stress-test.** Simulate a crossmatch failing the night before and re-solve. Sweep the survival rate $p$ from 1.0 to 0.5, compare India's blood-group mix with the US mix, and measure what a fairness rule for highly sensitised patients costs.
6. **Answer and package.** Report the survival rate below which 3-way rings stop being worth it, and build the demo, deck and design file around that answer.

The core maths. Choose a 0/1 variable for each candidate ring $c$, with weight $w_c$, so that no family appears in two chosen rings:

$$
\max \sum_{c \in \mathcal{C}_L} w_c \, x_c \quad \text{subject to} \quad \sum_{c \ni v} x_c \le 1 \;\; \text{for every family } v, \qquad x_c \in \{0, 1\}
$$

If every final crossmatch passes independently with probability $p$, a ring of size $|c|$ is worth its expected transplants:

$$
w_c = |c| \, p^{|c|}
$$

So a 3-family ring beats a 2-family swap on the same families only when

$$
3p^3 > 2p^2 \iff p > \tfrac{2}{3}
$$

With rings capped at 2 families the problem is a matching, solvable in polynomial time. Allowing 3-family rings makes it NP-hard (Abraham, Blum and Sandholm, 2007). That jump is the algorithm story of the talk.

## Macro plan

Five phases, each ending at a gate the whole team can check: understand, design, build, experiment, then tell the story.

**Timeline, 20 Oct to early December 2026:**

| Phase or gate | Dates |
| --- | --- |
| Understand the problem | 20 – 26 Oct |
| Design before code | 27 Oct – 2 Nov |
| ◆ Gate: pseudocode done | 2 Nov |
| Build the engine | 3 – 16 Nov |
| ◆ Gate: checks all green | 16 Nov |
| Run experiments | 17 – 23 Nov |
| ◆ **Feature freeze** | **23 Nov** |
| Deck, docs, rehearsals | 24 Nov – 7 Dec |

Code starts only after the design gate on 2 Nov; features freeze on 23 Nov.

Week 1 stays light for mid-sems. At each gate the lead decides whether we are on schedule or cut scope, using the cut lines below.

## Week-by-week tracker

Each week ends with a concrete check, so anyone can tell at a glance whether we are on track. Update the status as you go.

| Week | Milestone | Done when | Owner | Status |
| --- | --- | --- | --- | --- |
| 1 · 20–26 Oct | Understand the problem (light week for mid-sems) | Problem statement and assumptions v1 written; the 8-family pool solved by hand on paper | Everyone | In progress |
| 2 · 27 Oct–2 Nov | Design before code | Flowchart and pseudocode for every module committed with dates; class skeletons reviewed together | Everyone; lead reviews | Not started |
| 3 · 3–9 Nov | Engine v1 | Generator, graph, cycle finder, first-come baseline, greedy and ILP run; oracle checks pass on Glasgow pools | Lead, generator and matching owners | Not started |
| 4 · 10–16 Nov | Exact solvers and failure model | Matching, branch and bound, local search and failure-aware scoring done; every cross-check green on 1,000 random pools | Matching and heuristics owners, lead | Not started |
| 5 · 17–23 Nov | Experiments; feature freeze Sun 23 Nov | Survival-rate sweep, India vs US, fairness curve, runtime chart and the edge-case demo all rebuild from one command | Simulation owner, everyone | Not started |
| 6 · 24–30 Nov | Tell the story | Charts, deck, design file and AI log finished; first dry run done | Everyone | Not started |
| 7 · 1–7 Dec | Rehearse and submit | Three timed rehearsals under 10 minutes; clinical Q&A drill; code submitted | Everyone | Not started |

## Who does what

Every teammate owns one algorithm they wrote themselves and can explain on stage, so the grade does not rest on the lead alone.

| Role | Owns | Algorithm they write by hand |
| --- | --- | --- |
| Lead | Architecture and interfaces, the ILP and failure-aware objective, the kep\_solver oracle harness, integration, the optional web viewer | ILP formulation with expected-transplant weights |
| Generator owner | The pool generator classes, India and US calibration, sensitisation and spouse rules | Calibrated random pool generation |
| Matching owner | Cycle finder, exact 2-way matching, brute-force verifier, cross-checks against networkx | Depth-first cycle search; augmenting-path matching |
| Heuristics owner | Greedy, local search, branch and bound | Branch and bound with its bounding rule |
| Simulation owner | Night-before failure simulation and re-solve, fairness sweep, runtime benchmarks, all charts | Monte Carlo failure simulator |

Pair a teammate with the lead the moment recursion stalls. The fallback for the cycle finder is plain nested loops for 2- and 3-family rings.

## Decisions to lock in week 1

These six choices shape every result, so we fix them before writing code and test how much each one matters. The first four are the ones to argue on stage.

| Decision | Our default | Alternative | How we test whether it matters |
| --- | --- | --- | --- |
| Longest swap allowed | Rings of up to 3 families | 2 only, or 4 and more (India has done up to 10) | Run 4-family rings on pools of up to 100 and report the extra gain |
| Last-minute test failures | Every crossmatch passes independently with the same probability $p$ | Highly sensitised patients fail more often | A sensitisation-dependent failure variant |
| Women and sensitisation | Female patients more often highly sensitised; a wife receiving from her husband has a positive crossmatch about 33% of the time, against 11% for unrelated pairs | No difference by sex | Sweep the female high-sensitisation share from 10% to 40% |
| What we maximise | Expected transplants, every patient counted equally | Priority weights for sensitised patients, group O, women or waiting time | Add a fairness rule and measure the transplants it costs |
| One pool or many | One national pool, as NOTTO's portal now allows | Separate state pools | Split the pool four ways and count the transplants lost |
| Altruist donors | Left out of the core build | Chains started by an altruistic donor | A stretch goal; we say on stage that chains would change the answer |

How we frame it in class: every family already has a willing donor, and better matching only lets more of them go ahead. Clinicians and committees decide, not software. "Unmatched" means waiting for the next round. All patients are simulated.

## Risks and cut lines

The biggest risks are scope, not difficulty; each has an early warning we can spot by a specific week.

| Risk | Early warning | What we do |
| --- | --- | --- |
| Medical rabbit hole | Week-3 debates about tissue typing | The compatibility model is frozen in week 1; questions go into a "limitations" list |
| "You just called a solver" | Branch and bound still failing tests in week 4 | Lead pairs with the heuristics owner; the deck leads with hand-written code and calls the ILP the oracle |
| Tool breakage | A fresh install fails | Pin PuLP 2.9.0 and keep kep\_solver in its own environment; HiGHS as a fallback solver |
| Gender result is null or reversed | The prototype already shows women matched slightly more often inside the pool | Present it as a finding: the gap is in who enters the pool, not in the matcher |
| A teammate stuck on recursion | Cycle finder late in week 3 | Pair with the lead; fall back to nested loops for 2- and 3-family rings |
| Talk runs long | First dry run over 11 minutes | One ring picture, one crossover chart, and the maths kept to the three formulas above |

If we fall behind, drop in this order:

1. The Next.js web viewer
2. Altruist chains
3. The multi-round pool simulation
4. A hand-written blossom matching (keep the simpler augmenting-path version)
5. Branch and bound (keep matching, greedy and the ILP)

Never cut: the failure-aware scoring, the cross-checks against brute force and kep\_solver, or the edge-case demo.

## Sources

- [Supreme Court, Indian Society of Organ Transplantation v. Union of India (19 Nov 2025)](https://www.supremecourtcases.com/indian-society-of-organ-transplantation-v-union-of-india-and-others/): requests national swap guidelines
- [Delhi High Court, W.P.(C) 7473/2026 (26 May 2026)](https://delhihighcourt.nic.in/app/showFileJudgment/59626052026CW74732026_123111.pdf): the law does not bar swaps between more than two pairs
- [ThePrint on NOTTO's national portal (13 Aug 2026)](https://theprint.in/health/800-medical-colleges-capable-of-retrieving-organs-but-just-200-do-how-notto-aims-to-revamp-transplants/3013925/)
- [Kute et al., kidney and liver exchange in India, Lancet Regional Health SE Asia (2025)](https://doaj.org/article/14696faa1aba41eebc41609311d7cf00): 1,839 exchanges at 65 centres
- [The South First on NOTTO gender data](https://thesouthfirst.com/health/keralam-and-delhi-different-states-same-story-women-donate-more-kidneys-but-receive-fewer/): women 70.7% of living donors, 22.7% of recipients in 2025
- [Agrawal et al. (2014), ABO groups in 10,000 Indian donors](https://doi.org/10.4103/0973-6247.137452)
- [Saidman et al. (2006), the standard pool generator](https://stanford.edu/%7Ealroth/papers/SaidmanRothSonmezUnverDelmonico.Transplantation.2006.pdf)
- [Bromberger et al. (2017), sensitisation and women's access to transplants](https://doi.org/10.1681/ASN.2016101059)
- [Abraham, Blum and Sandholm (2007), NP-hardness of rings of 3 or more](https://home.ttic.edu/~avrim/Papers/ec150abraham.pdf)
- [Dickerson, Procaccia and Sandholm, failure-aware kidney exchange](https://arxiv.org/pdf/1606.01623)
- [Glasgow kidney-exchange benchmark pools (CC BY 4.0)](https://researchdata.gla.ac.uk/1213/)
- [kep\_solver on PyPI](https://pypi.org/project/kep-solver/)