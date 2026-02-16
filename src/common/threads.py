from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Process
from typing import Iterable

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
    iterable, worker, processes, initializer, initargs, desc="Processing", postfix=None
) -> list:
    with Pool(processes, initializer, initargs) as pool:
        return list(
            tqdm(
                pool.imap_unordered(worker, iterable),
                total=len(iterable),
                desc=desc,
                postfix=postfix,
            )
        )
