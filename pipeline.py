"""
KopiCheck prototype pipeline.

Takes a pre recorded test clip, samples key frames at a fixed interval
(rather than processing every frame, which is neither necessary nor
realistic on standard hardware), classifies each sampled frame against
the NEA checklist categories, and compiles the results into an end of
day compliance log in the format shown in the proposal deck.

This prototype processes a recorded clip rather than a live feed. The
live camera version, with real time prompting, is planned for the
semi final stage.
"""

import argparse
import json
import os
from datetime import datetime, timedelta

import cv2

from checklist import CHECKLIST_CATEGORIES, SEVERITY
from models import classify_frame

FRAME_DIR = "_sampled_frames"
PROMPT_PATH = os.path.join("prompts", "frame_classification.txt")


def sample_frames(video_path: str, interval_seconds: int) -> list[dict]:
    """
    Pull one frame every `interval_seconds` from the input video and
    save it to disk. Returns a list of {timestamp_seconds, frame_path}.
    """
    os.makedirs(FRAME_DIR, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = int(fps * interval_seconds)

    sampled = []
    frame_index = 0
    saved_index = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % frame_interval == 0:
            timestamp_seconds = frame_index / fps
            frame_path = os.path.join(FRAME_DIR, f"frame_{saved_index:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            sampled.append({
                "timestamp_seconds": timestamp_seconds,
                "frame_path": frame_path,
            })
            saved_index += 1

        frame_index += 1

    cap.release()
    return sampled


def classify_sampled_frames(sampled: list[dict], base_time: datetime) -> list[dict]:
    """
    Run each sampled frame through Qwen3-VL and attach a wall clock
    timestamp, using base_time as the assumed start of service.
    """
    with open(PROMPT_PATH, "r") as f:
        prompt = f.read()

    events = []
    for sample in sampled:
        result = classify_frame(sample["frame_path"], prompt)

        if result.get("category") == "none":
            continue

        event_time = base_time + timedelta(seconds=sample["timestamp_seconds"])
        confidence = result.get("confidence", 0.0)

        if confidence < 0.6:
            status = "flagged_for_review"
        elif result.get("flagged"):
            status = "flagged"
        else:
            status = "ok"

        events.append({
            "time": event_time.strftime("%H:%M"),
            "category": CHECKLIST_CATEGORIES.get(
                result["category"], {}
            ).get("label", result["category"]),
            "event": result.get("description", ""),
            "reading": result.get("reading"),
            "confidence": confidence,
            "status": status,
        })

    return events


def compile_log(events: list[dict], output_path: str) -> None:
    """
    Write the compiled end of day compliance log to a JSON file, in
    the same shape shown in the proposal deck's demo table.
    """
    log = {
        "generated_at": datetime.now().isoformat(timespec="minutes"),
        "checklist_categories_tracked": list(CHECKLIST_CATEGORIES.keys()),
        "severity_legend": SEVERITY,
        "events": events,
        "requires_owner_review": any(e["status"] != "ok" for e in events),
    }

    with open(output_path, "w") as f:
        json.dump(log, f, indent=2)

    print(f"Compiled {len(events)} events. Log written to {output_path}")
    if log["requires_owner_review"]:
        print("Some events need owner review before this log is final.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the KopiCheck prototype pipeline on a test clip.")
    parser.add_argument("--input", required=True, help="Path to the input video clip.")
    parser.add_argument("--output", default="output_log.json", help="Path to write the compiled log.")
    parser.add_argument("--interval", type=int, default=3, help="Seconds between sampled frames.")
    args = parser.parse_args()

    base_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    print(f"Sampling frames from {args.input} every {args.interval}s...")
    sampled = sample_frames(args.input, args.interval)
    print(f"Sampled {len(sampled)} frames.")

    print("Classifying frames against the NEA checklist...")
    events = classify_sampled_frames(sampled, base_time)

    compile_log(events, args.output)


if __name__ == "__main__":
    main()
