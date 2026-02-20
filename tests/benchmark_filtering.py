
import time
import timeit
from datetime import datetime, timedelta, timezone

SLACK_LIMIT_PERIOD = 1

def original_implementation(timestamps, cutoff):
    recent_timestamps = []
    for t in timestamps:
        # Ensure timestamp is timezone aware
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        if t > cutoff:
            recent_timestamps.append(t)
    return recent_timestamps

def optimized_implementation_1(timestamps, cutoff):
    # Using list comprehension with generator
    return [
        t for t in (
            t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
            for t in timestamps
        )
        if t > cutoff
    ]

def optimized_implementation_4(timestamps, cutoff):
    # Two passes: standardize then filter
    standardized = [
        t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
        for t in timestamps
    ]
    return [t for t in standardized if t > cutoff]

def run_benchmark():
    now = datetime.now(timezone.utc)
    # Keep most items
    cutoff = now - timedelta(days=365)

    # Generate data
    timestamps = []
    for i in range(100000):
        ts = now - timedelta(seconds=i)
        if i % 2 == 0:
            ts = ts.replace(tzinfo=None) # Make naive
        timestamps.append(ts)

    print(f"Benchmarking with {len(timestamps)} timestamps (keeping most)...")

    iterations = 50

    time_orig = timeit.timeit(lambda: original_implementation(timestamps, cutoff), number=iterations)
    print(f"Original: {time_orig:.4f}s")

    time_opt1 = timeit.timeit(lambda: optimized_implementation_1(timestamps, cutoff), number=iterations)
    print(f"Optimized 1 (GenExpr): {time_opt1:.4f}s")

    time_opt4 = timeit.timeit(lambda: optimized_implementation_4(timestamps, cutoff), number=iterations)
    print(f"Optimized 4 (Two-pass): {time_opt4:.4f}s")

    improvement_1 = (time_orig - time_opt1) / time_orig * 100
    print(f"Improvement 1: {improvement_1:.2f}%")

    improvement_4 = (time_orig - time_opt4) / time_orig * 100
    print(f"Improvement 4: {improvement_4:.2f}%")

if __name__ == "__main__":
    run_benchmark()
