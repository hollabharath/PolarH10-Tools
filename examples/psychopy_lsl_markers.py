#!/usr/bin/env python3
"""Minimal PsychoPy + pylsl marker outlet for event-locked Polar H10 ECG.

Workflow
--------
1. On the phone: Settings → enable "LSL ECG stream", start a recording
   (ECG must already be running before the task).
2. On the lab PC (same Wi‑Fi): open LabRecorder and confirm streams
   ``PolarH10_ECG`` and ``PsychoPyMarkers`` appear.
3. Run this script (or paste the marker helpers into your experiment).
4. Stop LabRecorder; analyse XDF (ECG aligned to TASK_START / STIM_ONSET / …).

Install (PC)::

    pip install pylsl psychopy

Visual timing tip: prefer ``win.callOnFlip(push_marker, "STIM_ONSET")`` so the
marker is stamped at the screen flip, not when Python requests the stimulus.
"""

from __future__ import annotations

import time

try:
    from pylsl import StreamInfo, StreamOutlet, local_clock
except ImportError as e:
    raise SystemExit("pip install pylsl") from e


def make_marker_outlet(name: str = "PsychoPyMarkers", source_id: str = "psychopy-1"):
    info = StreamInfo(
        name=name,
        type="Markers",
        channel_count=1,
        nominal_srate=0.0,  # irregular
        channel_format="string",
        source_id=source_id,
    )
    return StreamOutlet(info)


def push_marker(outlet: StreamOutlet, label: str, timestamp: float | None = None) -> None:
    """Push one string marker. timestamp=None → LSL local_clock() now."""
    ts = local_clock() if timestamp is None else float(timestamp)
    outlet.push_sample([str(label)], timestamp=ts)


def demo_without_psychopy(seconds: float = 8.0) -> None:
    """No display — just emit TASK_START / STIM_ONSET / RESPONSE / TASK_END."""
    outlet = make_marker_outlet()
    print("Marker outlet open. Start LabRecorder, then wait…")
    time.sleep(1.0)
    push_marker(outlet, "TASK_START")
    t0 = time.perf_counter()
    n = 0
    while time.perf_counter() - t0 < seconds:
        push_marker(outlet, "STIM_ONSET")
        time.sleep(0.8)
        push_marker(outlet, "RESPONSE")
        time.sleep(0.4)
        n += 1
    push_marker(outlet, "TASK_END")
    print(f"Done ({n} stim cycles).")


def demo_with_psychopy() -> None:
    from psychopy import core, visual  # type: ignore

    outlet = make_marker_outlet()
    win = visual.Window(fullscr=False, color="black")
    stim = visual.TextStim(win, text="+", color="white", height=0.15)

    push_marker(outlet, "TASK_START")
    for i in range(5):
        stim.text = f"STIM {i + 1}"
        # Stamp at flip for better visual timing.
        win.callOnFlip(push_marker, outlet, "STIM_ONSET")
        stim.draw()
        win.flip()
        core.wait(0.5)
        push_marker(outlet, "RESPONSE")
        core.wait(0.3)
    push_marker(outlet, "TASK_END")
    win.close()
    core.quit()


if __name__ == "__main__":
    import sys

    if "--psychopy" in sys.argv:
        demo_with_psychopy()
    else:
        demo_without_psychopy()
