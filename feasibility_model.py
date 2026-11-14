#!/usr/bin/env python3
"""
feasibility_model.py - sync-payload and cost model for joining distributed AI
training from Indonesia (gotong).

A small calculator around the dated public figures compiled in README.md. It
answers two questions with explicit, inspectable formulas:

  1. What does one synchronization event actually look like for a home node?
     The model derives the per-node payload of a gradient/pseudo-gradient
     exchange (ring all-reduce: 2 * (n-1)/n * params * bytes_per_param) and
     separates three quantities that are easy to conflate:
       - payload per sync event (GB)
       - time to transfer that payload at a given link speed
       - average bandwidth if the payload is spread over the whole interval
     A method that syncs 500x less often does NOT automatically need 500x
     less bandwidth at every moment; it sends a comparable payload, just
     less frequently.
  2. What does it cost per month to run a GPU node at home in Indonesia
     (power + internet + amortized hardware)?

Everything here is a MODEL over the dated figures in README.md (sources and
dates are in that file). Nothing was measured from an Indonesian home
connection by this project. The published Decoupled DiLoCo figure (840 Mbps)
came from Google's datacenter workload with enterprise links; it is shown
as a labeled reference point, not as evidence about home connections.
Override the defaults with your own numbers.

Python 3.9+, no third-party dependency for the calculations.
--viz needs matplotlib.

Usage:
    python3 feasibility_model.py                 # defaults (12B model example)
    python3 feasibility_model.py --params-b 3 --workers 16 --inner-steps 250
    python3 feasibility_model.py --viz feasibility.png
"""

import argparse

# --- Dated figures from README.md (see Sources there; re-check before relying) ---
# NOTE: these are INDONESIA-WIDE Ookla medians (Aug-Oct 2025), not Jakarta-only.
ID_MEDIAN_DOWN_MBPS = 39.9
ID_MEDIAN_UP_MBPS = 26.6
PLN_TARIFF_RP_PER_KWH = 1444.70     # 2025 residential tariff (low end of range)
FIBER_100MBPS_RP_MONTH = 250_000    # "from about Rp250k/month" ISP pages, 2025
STARLINK_RP_MONTH = 750_000         # top of Rp479-750k range, Oct 2025
STARLINK_HW_RP = 6_800_000          # mid of Rp5.9-7.8jt hardware, Oct 2025
USED_RTX3090_RP = 15_000_000        # mid of Rp12-19jt listings, Nov 2026
# Published reference points (different settings - do not compare directly):
# Decoupled DiLoCo measured 0.84 Gbps per node for a 12B model across four
# Google datacenter regions on 2-5 Gbps enterprise links (Apr 2026), where
# classic synchronous training needed 198 Gbps. Datacenter workload, not a
# home-internet measurement.
DECOUPLED_DILOCO_MBPS = 840
CLASSIC_PUBLISHED_GBPS = 198


def sync_payload_gb(params_b, bytes_per_param, workers, compression=1.0):
    """Per-node payload of one ring all-reduce sync event, in GB.

    Ring all-reduce moves ~2*(n-1)/n times the gradient per node per sync.
    `compression` scales the payload (e.g. 0.2 for Top-K 20% sparsification).
    """
    ring_factor = 2 * (workers - 1) / workers
    return ring_factor * params_b * 1e9 * bytes_per_param * compression / 1e9


def transfer_seconds(payload_gb, link_mbps):
    """Seconds to move `payload_gb` over a link of `link_mbps`."""
    return payload_gb * 1e9 * 8 / (link_mbps * 1e6)


def avg_rate_mbps(payload_gb, interval_s):
    """Average bandwidth if the payload is spread over `interval_s`."""
    return payload_gb * 1e9 * 8 / interval_s / 1e6


def monthly_power_rp(gpu_watt, hours_per_day, tariff=PLN_TARIFF_RP_PER_KWH):
    kwh = gpu_watt / 1000 * hours_per_day * 30
    return kwh * tariff, kwh


def fmt_rp(x):
    return f"Rp{x:,.0f}".replace(",", ".")


def cost_scenarios(amortize_months=24):
    """Monthly cost scenarios in Rp (hardware amortized over 24 months)."""
    power_rp, kwh = monthly_power_rp(500, 24)
    return {
        "GPU + power\n+ fiber (modeled)": {
            "GPU amortization (24 mo)": USED_RTX3090_RP / amortize_months,
            f"Power (~{kwh:.0f} kWh/mo)": power_rp,
            "Fiber ~100 Mbps": FIBER_100MBPS_RP_MONTH,
        },
        "GPU + power\n+ Starlink (modeled)": {
            "GPU amortization (24 mo)": USED_RTX3090_RP / amortize_months,
            f"Power (~{kwh:.0f} kWh/mo)": power_rp,
            "Starlink": STARLINK_RP_MONTH,
            "Starlink hardware (24 mo)": STARLINK_HW_RP / amortize_months,
        },
    }


def fmt_duration(seconds):
    if seconds >= 5400:
        return f"{seconds/3600:.1f} hours"
    if seconds >= 90:
        return f"{seconds/60:.0f} min"
    return f"{seconds:.0f} s"


def print_report(args):
    payload = sync_payload_gb(args.params_b, 2, args.workers, args.compression)
    interval_s = args.inner_steps * args.step_time
    sync_rate = avg_rate_mbps(payload, args.step_time)
    diloco_avg = avg_rate_mbps(payload, interval_s)
    t_median = transfer_seconds(payload, ID_MEDIAN_UP_MBPS)
    t_100 = transfer_seconds(payload, 100)
    t_1000 = transfer_seconds(payload, 1000)
    config = (f"{args.params_b}B params, compression x{args.compression}, "
              f"H={args.inner_steps}")

    print(f"MODEL ASSUMPTIONS: {args.params_b}B params, fp16 (2 bytes/param), "
          f"ring all-reduce across {args.workers} workers "
          f"(factor 2*(n-1)/n = {2*(args.workers-1)/args.workers:.2f}), "
          f"{args.step_time}s/step, H={args.inner_steps} inner steps "
          f"(outer interval {interval_s:.0f}s), compression x{args.compression}")
    print("(indicative formulas; not a measurement)\n")
    print("ONE SYNC EVENT PER NODE")
    print(f"  payload: {payload:.2f} GB")
    print(f"  transfer time at Indonesia-wide median upload "
          f"({ID_MEDIAN_UP_MBPS} Mbps): {fmt_duration(t_median)}")
    print(f"  transfer time at a hypothetical 100 Mbps upload: "
          f"{fmt_duration(t_100)}; at 1 Gbps: {fmt_duration(t_1000)}")
    print(f"  outer interval (H x step time): {fmt_duration(interval_s)}\n")
    print("BANDWIDTH, KEPT HONEST")
    gap = sync_rate / ID_MEDIAN_UP_MBPS
    print(f"  Synchronous (payload every step): {sync_rate/1000:,.1f} Gbps "
          f"sustained - ~{gap:,.0f}x the Indonesia-wide median upload.")
    print(f"    (Published datacenter reference: {CLASSIC_PUBLISHED_GBPS} Gbps "
          f"for 12B in Google's setting.)")
    print(f"  DiLoCo-style average over the outer interval: {diloco_avg:,.1f} Mbps.")
    print("    This is an AVERAGE: the payload still has to physically move.")
    if t_median <= interval_s:
        print(f"    At the median upload the transfer ({fmt_duration(t_median)}) "
              f"fits inside the {fmt_duration(interval_s)} interval for this")
        print(f"    configuration ({config}).")
    else:
        print(f"    At the median upload the transfer ({fmt_duration(t_median)}) "
              f"outlasts the {fmt_duration(interval_s)} interval by "
              f"~{t_median/interval_s:.1f}x for this configuration ({config}):")
        print("    the node cannot keep up. Shrinking the payload, a smaller")
        print("    model, or a longer interval changes this - rerun with those.")
    if t_1000 > interval_s:
        print(f"    Even a 1 Gbps upload ({fmt_duration(t_1000)}) would not keep "
              f"up for this configuration.")
    print(f"  Decoupled DiLoCo's {DECOUPLED_DILOCO_MBPS} Mbps is a measured point from")
    print("    Google's datacenters (12B, 4 regions, 2-5 Gbps enterprise links) -")
    print("    shown for scale only; it is not evidence about home connections.\n")
    print("MONTHLY COST SCENARIOS - GPU amortization + modeled power + network")
    print("ONLY. Excludes the rest of the rig (CPU/board/RAM/storage), tax,")
    print("cooling and maintenance. The used-GPU price is not a claim that a rig")
    print("capable of full 12B training is feasible at that price.")
    for name, items in cost_scenarios().items():
        total = sum(items.values())
        print(f"  {name.replace(chr(10), ' ')}: ~{fmt_rp(total)}/month")
        for k, v in items.items():
            print(f"    - {k}: {fmt_rp(v)}")
    print("\n  Reminder: crypto incentives are unproven as income; treat any offset")
    print("  as experiment, not earnings (see README).")


def make_viz(args, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    payload = sync_payload_gb(args.params_b, 2, args.workers, args.compression)
    interval_min = args.inner_steps * args.step_time / 60

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- Panel A: transfer time of one sync payload vs the outer interval ---
    links = [("Indonesia-wide median upload\n26.6 Mbps (Ookla, Aug-Oct 2025)",
              ID_MEDIAN_UP_MBPS),
             ("100 Mbps upload\n(hypothetical)", 100),
             ("1 Gbps upload\n(hypothetical)", 1000)]
    names = [n for n, _ in links]
    minutes = [transfer_seconds(payload, mbps) / 60 for _, mbps in links]
    colors = ["#c0392b" if m > interval_min else "#27ae60" for m in minutes]
    bars = ax1.barh(names, minutes, color=colors)
    ax1.set_xscale("log")
    ax1.set_xlabel("minutes to transfer one sync payload (log scale)")
    ax1.axvline(interval_min, color="#2c3e50", ls="--",
                label=f"outer interval H={args.inner_steps} x "
                      f"{args.step_time}s = {interval_min:.1f} min")
    for b, v in zip(bars, minutes):
        label = f"{v/60:.1f} h" if v >= 90 else f"{v:.0f} min"
        ax1.text(v * 1.15, b.get_y() + b.get_height() / 2, label,
                 va="center", fontsize=9)
    ax1.legend(fontsize=8, loc="lower right")
    ax1.set_title(
        f"One sync event: {payload:.0f} GB/node "
        f"({args.params_b}B fp16, ring all-reduce, {args.workers} workers)\n"
        "red = transfer outlasts the outer interval (model, not measured)",
        fontsize=10)

    # --- Panel B: monthly cost, plain million-Rp tick labels ---
    scenarios = cost_scenarios()
    x = range(len(scenarios))
    item_colors = {
        "GPU amortization (24 mo)": "#2980b9",
        "Power (~360 kWh/mo)": "#e67e22",
        "Fiber ~100 Mbps": "#27ae60",
        "Starlink": "#8e44ad",
        "Starlink hardware (24 mo)": "#c39bd3",
    }
    labeled = set()
    for i, (name, items) in enumerate(scenarios.items()):
        bottom = 0
        for k, v in items.items():
            ax2.bar(i, v, bottom=bottom, color=item_colors.get(k, "#7f8c8d"),
                    label=k if k not in labeled else None, width=0.55)
            labeled.add(k)
            bottom += v
        ax2.text(i, bottom + 40000, fmt_rp(bottom), ha="center", fontsize=9,
                 weight="bold")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(list(scenarios.keys()), fontsize=9)
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1e6:.1f}"))
    ax2.set_ylabel("Rp per month (millions)")
    ax2.set_ylim(0, max(sum(s.values()) for s in scenarios.values()) * 1.25)
    ax2.legend(fontsize=8)
    ax2.set_title("Monthly cost: GPU amortization + modeled power + network\n"
                  "(excludes rest of rig, tax, cooling; dated 2025-2026 figures)",
                  fontsize=10)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    return path


def main():
    import math

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--params-b", type=float, default=12.0,
                    help="model size in billions of parameters (default 12)")
    ap.add_argument("--workers", type=int, default=8,
                    help="nodes in the ring all-reduce (default 8)")
    ap.add_argument("--step-time", type=float, default=2.0,
                    help="seconds per training step (default 2.0)")
    ap.add_argument("--inner-steps", type=int, default=500,
                    help="DiLoCo inner steps H between syncs (default 500)")
    ap.add_argument("--compression", type=float, default=1.0,
                    help="payload scale factor in (0, 1], e.g. 0.2 for Top-K 20%%")
    ap.add_argument("--viz", metavar="PNG", help="write charts to this path")
    args = ap.parse_args()
    for name, val in (("--params-b", args.params_b),
                      ("--step-time", args.step_time),
                      ("--compression", args.compression)):
        if not math.isfinite(val) or val <= 0:
            ap.error(f"{name} must be a finite number > 0")
    if args.compression > 1:
        ap.error("--compression must be <= 1.0")
    if args.workers < 2:
        ap.error("--workers must be >= 2")
    if args.inner_steps < 1:
        ap.error("--inner-steps must be >= 1")
    print_report(args)
    if args.viz:
        print(f"\nCharts written to {make_viz(args, args.viz)}")


if __name__ == "__main__":
    main()
