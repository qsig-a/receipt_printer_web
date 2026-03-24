import time
import timeit
from datetime import datetime, timedelta, timezone

def original(timestamps, cutoff):
    return [
        t for t in [
            t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
            for t in timestamps
        ]
        if t > cutoff
    ]

def optimized_loop(timestamps, cutoff):
    recent = []
    for t in timestamps:
        t_utc = t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
        if t_utc > cutoff:
            recent.append(t_utc)
    return recent

def optimized_gen(timestamps, cutoff):
    return [
        t_utc
        for t in timestamps
        if (t_utc := t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t) > cutoff
    ]

def optimized_simple_comprehension(timestamps, cutoff):
    return [
        t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t
        for t in timestamps
    ]

now = datetime.now(timezone.utc)
cutoff = now - timedelta(minutes=1)

# Generate a mix of recent and old timestamps, with and without tzinfo
timestamps = []
for i in range(100):
    t = now - timedelta(seconds=i*2)
    if i % 2 == 0:
        t = t.replace(tzinfo=None)
    timestamps.append(t)


print("Original:")
orig_time = timeit.timeit(lambda: original(timestamps, cutoff), number=100000)
print(orig_time)

print("Optimized (loop):")
loop_time = timeit.timeit(lambda: optimized_loop(timestamps, cutoff), number=100000)
print(loop_time)

print("Optimized (generator expression/walrus):")
gen_time = timeit.timeit(lambda: optimized_gen(timestamps, cutoff), number=100000)
print(gen_time)

print(f"Improvement (loop): {(orig_time - loop_time) / orig_time * 100:.2f}%")
print(f"Improvement (gen): {(orig_time - gen_time) / orig_time * 100:.2f}%")
