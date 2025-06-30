from multiprocessing.pool import ThreadPool
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
