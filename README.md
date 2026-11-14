# Distributed AI training from Jakarta: feasibility notes

Research notes on how feasible distributed AI training is from Jakarta, Indonesia, and how people can contribute. Compiled 15 November 2026 from public sources, linked at the bottom. Nothing here was measured from an Indonesian home connection; figures are dated where they appear.

## The short answer

Feasible to join from Jakarta, with one honest caveat: the lightest door (a Petals server) is verifiably open today, while the big headline runs are gated or between rounds. The low-communication training methods behind them need home-internet bandwidth rather than datacenter interconnects, and Jakarta's connectivity clears that bar on paper. Running a Jakarta-organized large training run is unproven.

## Why this became possible

Classic training synchronizes chips inside one datacenter at 400+ Gbps. Five developments cut that requirement by orders of magnitude. Note which are proven where:

1. **DiLoCo (Google DeepMind, 2023).** Trains one model across "islands" of poorly connected machines, syncing only every 500 steps: 500x less communication, same quality. Proven in lab experiments.
2. **INTELLECT-2 (Prime Intellect, 2025).** The real-world proof: a 32B model trained over the internet by volunteers' GPUs, permissionless. Its asynchronous design removed communication as the bottleneck; a rig with 4x RTX 3090 was enough to join. This run has concluded; it was RL post-training, not pretraining.
3. **Psyche (Nous Research, 2025).** DisTrO cuts data transfer by orders of magnitude for pretraining over the internet. Its 40B "Consilience" run produced a public checkpoint. Joining is gated today: participation requires the run admin's run-manager binary and a wallet the admin authorizes; no self-serve enrollment verified.
4. **Decoupled DiLoCo (DeepMind, April 2026).** 0.84 Gbps where classic training needs 198 Gbps, but note the setting: Google's own datacenters, a 12B model across four US regions on 2-5 Gbps enterprise links. Datacenter-to-datacenter, not home-to-home.
5. **MIRI feasibility model (May 2026).** A simulation, not a measurement: modeled consumer-grade internet (100 Mbps, 100 ms latency) and found distributed training about 3x the cost of a datacenter run, with latency barely mattering. Plausible, but not measured from Jakarta.

## The Jakarta reality check

These are dated background figures, not current quotes; re-check before acting on them.

- Fixed broadband median: 39.9 Mbps down, 26.6 Mbps up, 7 ms latency. Indonesia-wide Ookla measurements, Aug-Oct 2025. South Jakarta and Bekasi were Indonesia's fastest cities in the same measurements.
- Jakarta to Singapore: about 13 ms ping (measured samples, May 2026).
- Home fiber: from about Rp250k/month in Jakarta; 100 Mbps plans common (ISP pricing pages, 2025).
- Starlink: Rp479-750k/month plus Rp5.9-7.8jt hardware (Oct 2025 pricing); aimed at areas without fiber.
- Indonesia ranked 116th worldwide on fixed broadband in 2025; a median means half of connections are slower.
- Used RTX 3090 (24 GB): about Rp12-19jt on Indonesian marketplaces (Nov 2026 listings). New high-end cards still 50%+ over global MSRP locally (retail reporting, Jul 2025).
- Power per GPU at 24/7: about Rp0.5-0.6jt/month, assuming a 500W rig running nonstop (360 kWh) at Rp1,444.70-1,699.53/kWh (2025 PLN residential tariffs, held flat that year). Apartment units are often billed through building management at different rates.
- Local quirk: Indonesian home ISPs commonly put subscribers behind CGNAT, so no direct incoming connections. Community reports say swarms still work via relays or Tailscale, but expect setup effort, and check the plan's fair-use policy before pushing upload 24/7.

## Lending a GPU while gaming

Full training and gaming don't share one GPU well. Throttled or small jobs can share it, at a cost. Idle-time lending is the honest default.

- A training client at full load uses nearly all compute cores and VRAM. A game on the same GPU drops to slideshow frame rates or crashes out of memory. That is "impractical", not "impossible".
- The middle ground exists but degrades both sides: cap GPU power or clocks, limit the client's VRAM share, accept lower frame rates.
- Small serving jobs are the realistic exception: a Petals-style server fits in 4+ GB VRAM and can leave enough room for lighter games.
- The clean pattern is idle-time: run the client overnight, stop it when you sit down to play. Psyche explicitly lets clients join or leave at any epoch, and DiLoCo-style methods are built to survive nodes dropping out.
- OS friction: Psyche's production client is Linux-only (macOS for development only). A Windows gaming rig means dual boot or WSL2 workarounds.
- Volunteers run third-party code, usually in Docker. Docker reduces the risk to the machine but is not a security guarantee; the networks' verification schemes protect the run from cheaters, not the host from the code.

## Three different things get called "distributed training"

1. **Training one model together.** The hard version. Volunteer swarms have done it at about 1B scale (Training Transformers Together, 2021); the 32B-40B internet runs were organized by funded teams that volunteers joined.
2. **Pooling machines for separate jobs.** A community co-op where members run their own jobs on shared hardware. Technically simpler (judgment call): no synchronized model state to keep consistent across the internet.
3. **Sharing inference.** Running trained models for others. Likely the easiest fit for home hardware: it needs the least coordination, and the experts quoted in the Span "mini data centers" article make the same call, saying training stays centralized while inference spreads out.

## How people can contribute

Checked 15 Nov 2026 for what is actually open, ordered roughly by how open the door is (judgment from each project's published requirements):

1. **Petals server — open today.** Self-serve: any GPU with 4+ GB VRAM hosts blocks of a shared model, serving inference and adapter-based fine-tuning, not full training. The public swarm is live, and its health monitor shows some models short on servers.
2. **Psyche / NousNet — gated.** Joining a run requires the run-manager binary distributed by the run admin plus a wallet they authorize. Clients can then join or leave at any epoch. No public self-serve enrollment verified.
3. **Prime Intellect ecosystem — code only, for now.** INTELLECT-2's permissionless run has ended and no new open run is announced. Open now: the prime-rl codebase and the Environments Hub with 500+ community-built RL tasks, which needs no GPU to contribute to.
4. **Gensyn node — paused.** The testnet accepts anything from a laptop to an H100, but its flagship RL Swarm was paused as of checking.
5. **Data and evaluation — open, no GPU.** SEACrowd is a grassroots community building Indonesian and regional language datasets; 20 contribution points earns paper co-authorship.
6. **Code — open, no GPU.** hivemind, prime-rl and Psyche are open source on GitHub; the Environments Hub is also code contribution.
7. **Organize locally — open, no GPU.** PythonID, AI for Indonesia and Build Club Jakarta are active communities where a study group or shared cluster could start.

## About that "sanctions" paper

The MIRI paper (*Does Distributed Training Undermine Compute Governance?*, May 2026) is about compute governance, not sanctions in the everyday sense. It asks whether future or proposed rules (EU AI Act training thresholds, California's SB 53, a proposed international treaty) could be evaded by spreading one big training run across many small nodes that each stay under the monitoring threshold. Its modeled answer: yes, in principle. About 101 small nodes could reach GPT-4-scale compute, 625 nodes a Llama-405B-scale run, at an estimated $31M of hardware for EU-scale thresholds.

Scope matters. The paper's evader is a well-resourced developer hiding frontier-scale work from regulators; it says nothing about individuals joining public research runs. Separately, US export controls restrict physical chip shipments to particular countries and increasingly scrutinize remote compute access, but this research found no rule that clearly addresses an Indonesian hobbyist contributing compute to an open run — and that is a gap, not a clearance. US AI export rules changed during 2025 and may change again. If a real project forms, that is the moment for a proper legal check. None of this is legal advice.

## Caveats and unknowns

- The strongest evidence (INTELLECT-2) is one completed RL run. The biggest claims (40B pretraining over the internet, DiLoCo at frontier scale) come from the teams proposing them, with limited independent replication.
- The MIRI numbers are simulation output, and the Decoupled DiLoCo numbers are from Google's datacenters. Neither was measured from an Indonesian home connection.
- Whether any large training run is accepting new contributors right now is unverified beyond what each project's docs said on 15 Nov 2026; enrollment gates change without notice.
- Crypto incentives (Solana fees, testnet points) are unproven as income. Treat them as experiment, not earnings.

## Sources

Methods and runs:
- Decoupled DiLoCo: https://deepmind.google/blog/decoupled-diloco/
- DiLoCo paper: https://arxiv.org/abs/2311.08105
- INTELLECT-2: https://www.primeintellect.ai/blog/intellect-2
- INTELLECT-3: https://www.primeintellect.ai/blog/intellect-3
- Nous Psyche overview: https://nousresearch.com/nous-psyche
- Psyche: joining a run: https://docs.psyche.network/enduser/join-run.html
- Psyche client FAQ: https://docs.psyche.network/enduser/client-faq.html
- MIRI paper: https://arxiv.org/abs/2605.29359
- Training Transformers Together (2021): https://training-transformers-together.github.io/

Join or contribute:
- Petals: https://github.com/bigscience-workshop/petals
- Petals swarm health: https://health.petals.dev
- Gensyn RL Swarm status: https://docs.gensyn.ai/testnet/rl-swarm
- SEACrowd: https://seacrowd.org/contribute.html

Jakarta figures:
- Ookla speeds via Katadata: https://katadata.co.id/digital/teknologi/692d4228f2204/kecepatan-internet-indonesia-melonjak-bekasi-dan-jakarta-selatan-tercepat
- Jakarta-Singapore ping: https://wondernetwork.com/pings/Jakarta/Singapore
- PLN tariff tables: https://tariflistrik.com/tarif-history/2025-01-01~2025-03-31
- Starlink pricing via Bisnis: https://teknologi.bisnis.com/read/20251022/101/1922503/menkomdigi-putar-otak-cari-layanan-internet-yang-lebih-murah-dari-starlink
- Used RTX 3090 listings: https://biggo.id/s/rtx%203090%20second
- GPU retail pricing report: https://www.murdockcruz.com/2025/07/07/harga-vga-baru-2025-masih-gila-rtx-5090-5080-naik-lebih-dari-50-dari-msrp/
- Span homes as mini data centers (Scientific American via Yahoo): https://tech.yahoo.com/ai/articles/span-wants-turn-homes-mini-120000696.html
