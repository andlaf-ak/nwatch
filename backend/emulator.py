"""Step emulator for testing nwwatch UI.

Creates and updates step JSON files to simulate a real nWave workflow.
"""

import argparse
import json
import os
import random
import shutil
import time
from pathlib import Path

# Sample phases and descriptions for realistic simulation
PHASES = ["research", "design", "implement", "test", "deploy"]

DESCRIPTIONS = {
    "research": [
        "Analyze existing codebase structure",
        "Research best practices for implementation",
        "Identify dependencies and constraints",
        "Review related documentation",
    ],
    "design": [
        "Design component architecture",
        "Define API contracts",
        "Create data models",
        "Plan integration points",
    ],
    "implement": [
        "Implement core functionality",
        "Add error handling",
        "Create unit tests",
        "Refactor for clarity",
        "Add logging and monitoring",
    ],
    "test": [
        "Run integration tests",
        "Perform load testing",
        "Validate edge cases",
        "Fix failing tests",
    ],
    "deploy": [
        "Prepare deployment configuration",
        "Deploy to staging environment",
        "Run smoke tests",
        "Deploy to production",
    ],
}


def create_step_file(folder: Path, task_id: str, project_id: str, phase: str, description: str, status: str) -> None:
    """Create a step JSON file."""
    data = {
        "task_id": task_id,
        "project_id": project_id,
        "phase": phase,
        "description": description,
        "validation": {
            "status": status
        }
    }

    file_path = folder / f"{task_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"  [{status.upper():11}] {task_id}: {description[:50]}...")


def update_step_status(folder: Path, task_id: str, new_status: str) -> None:
    """Update the status of an existing step file."""
    file_path = folder / f"{task_id}.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    old_status = data["validation"]["status"]
    data["validation"]["status"] = new_status

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"  [{old_status.upper():11}] -> [{new_status.upper():11}] {task_id}")


def generate_steps(num_steps: int = 15) -> list[dict]:
    """Generate a list of step definitions."""
    steps = []
    major = 1
    minor = 1

    for phase in PHASES:
        descriptions = DESCRIPTIONS[phase]
        num_phase_steps = min(len(descriptions), num_steps // len(PHASES) + 1)

        for i in range(num_phase_steps):
            if len(steps) >= num_steps:
                break

            task_id = f"{major:02d}-{minor:02d}"
            steps.append({
                "task_id": task_id,
                "phase": phase,
                "description": descriptions[i % len(descriptions)],
            })
            minor += 1

        major += 1
        minor = 1

    return steps[:num_steps]


def run_simulation(folder: Path, project_id: str, num_steps: int, delay: float, failure_rate: float) -> None:
    """Run the step simulation."""

    # Clean and create folder
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)

    print(f"\nStarting simulation in: {folder}")
    print(f"Project: {project_id}")
    print(f"Steps: {num_steps}, Delay: {delay}s, Failure rate: {failure_rate*100:.0f}%\n")

    steps = generate_steps(num_steps)

    # Phase 1: Create all steps as pending
    print("Creating initial steps (all pending)...")
    for step in steps:
        create_step_file(
            folder,
            step["task_id"],
            project_id,
            step["phase"],
            step["description"],
            "pending"
        )
        time.sleep(0.1)  # Small delay for visual effect

    print(f"\nCreated {len(steps)} steps. Starting workflow simulation...\n")
    time.sleep(delay)

    # Phase 2: Progress through steps
    for i, step in enumerate(steps):
        task_id = step["task_id"]

        # Set current step to in_progress
        print(f"\nStep {i+1}/{len(steps)}: {task_id}")
        update_step_status(folder, task_id, "in_progress")

        # Simulate work being done
        work_time = delay * random.uniform(0.5, 1.5)
        time.sleep(work_time)

        # Determine outcome
        if random.random() < failure_rate:
            # Step failed
            update_step_status(folder, task_id, "failed")
            print(f"  Step {task_id} failed! Retrying...")
            time.sleep(delay * 0.5)

            # Retry: back to in_progress
            update_step_status(folder, task_id, "in_progress")
            time.sleep(delay * 0.5)

            # 80% chance to succeed on retry
            if random.random() < 0.8:
                update_step_status(folder, task_id, "completed")
            else:
                update_step_status(folder, task_id, "skipped")
                print(f"  Step {task_id} skipped after retry failure")
        else:
            # Step completed successfully
            update_step_status(folder, task_id, "completed")

    print("\n" + "=" * 50)
    print("Simulation complete!")
    print("=" * 50)


def run_interactive(folder: Path, project_id: str, num_steps: int) -> None:
    """Run in interactive mode - user controls progression."""

    # Clean and create folder
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)

    print(f"\nInteractive mode - folder: {folder}")
    print(f"Project: {project_id}\n")

    steps = generate_steps(num_steps)

    # Create all steps as pending
    print("Creating initial steps...")
    for step in steps:
        create_step_file(
            folder,
            step["task_id"],
            project_id,
            step["phase"],
            step["description"],
            "pending"
        )

    print(f"\nCreated {len(steps)} steps.\n")
    print("Commands:")
    print("  n / next     - Move to next step (complete current, start next)")
    print("  f / fail     - Fail current step")
    print("  s / skip     - Skip current step")
    print("  a / auto     - Switch to automatic mode (continue without interaction)")
    print("  r / restart  - Restart simulation")
    print("  q / quit     - Exit\n")

    current_idx = 0

    # Start first step
    update_step_status(folder, steps[0]["task_id"], "in_progress")
    print(f"Current step: {steps[0]['task_id']} - {steps[0]['description']}\n")

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if cmd in ("q", "quit", "exit"):
            print("Exiting...")
            break

        elif cmd in ("n", "next"):
            if current_idx < len(steps):
                # Complete current step
                update_step_status(folder, steps[current_idx]["task_id"], "completed")
                current_idx += 1

                if current_idx < len(steps):
                    # Start next step
                    update_step_status(folder, steps[current_idx]["task_id"], "in_progress")
                    print(f"Current step: {steps[current_idx]['task_id']} - {steps[current_idx]['description']}\n")
                else:
                    print("\nAll steps completed!")

        elif cmd in ("f", "fail"):
            if current_idx < len(steps):
                update_step_status(folder, steps[current_idx]["task_id"], "failed")
                print(f"Step {steps[current_idx]['task_id']} marked as failed. Use 'n' to retry or 's' to skip.\n")

        elif cmd in ("s", "skip"):
            if current_idx < len(steps):
                update_step_status(folder, steps[current_idx]["task_id"], "skipped")
                current_idx += 1

                if current_idx < len(steps):
                    update_step_status(folder, steps[current_idx]["task_id"], "in_progress")
                    print(f"Current step: {steps[current_idx]['task_id']} - {steps[current_idx]['description']}\n")
                else:
                    print("\nAll steps processed!")

        elif cmd in ("a", "auto"):
            print("\nSwitching to automatic mode...\n")
            # Continue from current step automatically
            delay = 2.0
            while current_idx < len(steps):
                task_id = steps[current_idx]["task_id"]
                print(f"Step {current_idx + 1}/{len(steps)}: {task_id}")

                # Complete current step
                update_step_status(folder, steps[current_idx]["task_id"], "completed")
                current_idx += 1

                if current_idx < len(steps):
                    # Start next step
                    time.sleep(delay * 0.5)
                    update_step_status(folder, steps[current_idx]["task_id"], "in_progress")
                    time.sleep(delay * 0.5)

            print("\nAll steps completed!")
            break

        elif cmd in ("r", "restart"):
            print("\nRestarting simulation...\n")
            run_interactive(folder, project_id, num_steps)
            break

        else:
            print("Unknown command. Use: n(ext), f(ail), s(kip), a(uto), r(estart), q(uit)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emulate nWave step progression for testing nwwatch UI"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Folder to create step files in"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default="test-project",
        help="Project ID (default: test-project)"
    )
    parser.add_argument(
        "--steps",
        "-n",
        type=int,
        default=15,
        help="Number of steps to create (default: 15)"
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=2.0,
        help="Delay between step transitions in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--failure-rate",
        "-f",
        type=float,
        default=0.1,
        help="Probability of step failure (0.0-1.0, default: 0.1)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (manual step progression)"
    )

    args = parser.parse_args()
    folder = Path(args.folder).resolve()

    try:
        if args.interactive:
            run_interactive(folder, args.project, args.steps)
        else:
            run_simulation(folder, args.project, args.steps, args.delay, args.failure_rate)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted.")


if __name__ == "__main__":
    main()
