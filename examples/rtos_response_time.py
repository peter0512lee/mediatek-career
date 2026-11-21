"""Explore the blocking budget of the chapter's fixed-priority control task."""

import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blocking_us", type=int, help="control-task blocking bound in microseconds")
    args = parser.parse_args()
    if args.blocking_us < 0:
        parser.error("blocking_us must be non-negative")

    # RX is the only higher-priority task; all times are in microseconds.
    rx_period = 1000
    rx_execution = 300
    control_execution = 650
    deadline = 1800
    base = control_execution + args.blocking_us
    window = base
    print(f"B={args.blocking_us} us, D={deadline} us")

    step = 0
    while True:
        print(f"R[{step}]={window} us")
        if window > deadline:
            print("Deadline not guaranteed: iteration exceeded D.")
            return
        rx_jobs = (window + rx_period - 1) // rx_period
        next_window = base + rx_jobs * rx_execution
        if next_window == window:
            print(f"Deadline met in the model: R={window} us.")
            return
        window = next_window
        step += 1


if __name__ == "__main__":
    main()
