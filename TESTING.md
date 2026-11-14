# Testing and dependencies

Python 3.9+. Analysis: standard library only. Charts: matplotlib.

Commands run and verified (2026-11-15, Python 3.10):

    python3 feasibility_model.py
    python3 feasibility_model.py --params-b 3 --workers 16 --inner-steps 250
    python3 feasibility_model.py --params-b 0.5 --compression 0.05 --inner-steps 1000
    python3 feasibility_model.py --viz feasibility.png
    python3 feasibility_model.py --workers 1      # rejected: must be >= 2
    python3 feasibility_model.py --params-b -3    # rejected: must be > 0
    python3 feasibility_model.py --params-b nan   # rejected: must be finite
    python3 feasibility_model.py --compression 0  # rejected
    python3 feasibility_model.py --compression 1.5  # rejected: must be <= 1
    python3 feasibility_model.py --step-time 0    # rejected
    python3 feasibility_model.py --inner-steps 0  # rejected

Verified behavior: prints model assumptions (params, bytes/param, ring
all-reduce factor with worker count, step time, H), the per-node sync payload,
transfer times at three link speeds, and average vs sustained rates with the
average/peak distinction explicit. Conclusions are computed from the inputs:
the default 12B configuration reports the transfer outlasting the outer
interval (~12.6x), while a tiny/compressed configuration (0.5B, x0.05, H=1000)
correctly reports the transfer fitting inside the interval. Monthly cost
scenarios are labeled GPU amortization + modeled power + network only. The published
Decoupled DiLoCo point is labeled as a datacenter measurement, shown for
scale only. Chart pixels inspected; the cost axis uses plain million-Rp tick
labels. All bandwidth medians are labeled Indonesia-wide (Ookla, Aug-Oct
2025), not Jakarta-specific.

The Pages site (docs/) was rendered headless and inspected at 1280px and
390px widths.
