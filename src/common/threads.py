from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Process
from typing import Iterable

from tqdm import tqdm

DEFAULT_WORKERS = 16


def run_with_threads(
    iterable, function, workers=DEFAULT_WORKERS, desc="Processing", status_order=None
) -> list:
    counts = {status: 0 for status, _ in status_order or []}
    with ThreadPool(workers) as pool:
        progress = tqdm(
            pool.imap_unordered(function, iterable),
            total=len(iterable),
            desc=desc,
        )
        results = []
        for result in progress:
            results.append(result)
            if status_order:
                counts[result.status] = counts.get(result.status, 0) + 1
                progress.set_postfix_str(
                    " | ".join(
                        f"{icon} {counts[status]}" for status, icon in status_order
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
