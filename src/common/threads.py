from multiprocessing.pool import ThreadPool
from multiprocessing import Pool,Process

from tqdm import tqdm

DEFAULT_WORKERS = 16


def run_with_threads(
    iterable, function, workers=DEFAULT_WORKERS, desc="Processing"
) -> list:
    with ThreadPool(workers) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(function, iterable),
                total=len(iterable),
                desc=desc,
            )
        )
    return results


def run_with_multiprocessing(
    iterable, function, workers=DEFAULT_WORKERS, desc="Processing"
) -> list:
    """
    Run function over iterable using multiprocessing.Pool (process-based parallelism).
    API matches run_with_threads.
    """
    with Pool(processes=workers) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(function, iterable),
                total=len(iterable),
                desc=desc,
            )
        )
    return results



if __name__ == "__main__":
    def callback(num):
        print(f"Hello from process {num}")

    run_with_multiprocessing(range(10), callback, workers=4, desc="Test Multiprocessing")