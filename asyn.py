import concurrent.futures

# Shared counter
import time

count = 0

# Function to increment the counter
def increment_counter():
    global count
    time.sleep(1)
    count=count+1
    print(count)

# Number of worker threads
num_workers = 8

# Create a ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Submit the increment_counter function to the executor multiple times
    futures = [executor.submit(increment_counter) for _ in range(100)]

    # Wait for all tasks to complete and retrieve their results
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

# Print the final value of the counter
print("Final count:", count)