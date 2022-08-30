"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import random
import time
from concurrent import futures

from tqdm import tqdm

from ml_git import log
from ml_git.constants import POOL_CLASS_NAME
from ml_git.ml_git_message import output_messages


def pool_factory(ctx_factory=None, nworkers=os.cpu_count() * 5, retry=2, pb_elts=None, pb_desc='units', fail_limit=None):
    log.debug(output_messages['DEBUG_CREATE_WORKER_POOL'] % (nworkers, retry),
              class_name=POOL_CLASS_NAME)
    ctxs = [ctx_factory() for i in range(nworkers)] if ctx_factory is not None else None
    return WorkerPool(nworkers=nworkers, pool_ctxs=ctxs, retry=retry, pb_elts=pb_elts, pb_desc=pb_desc, fail_limit=fail_limit)


class WorkerPool(object):
    def __init__(self, nworkers=10, pool_ctxs=None, retry=0, pb_elts=None, pb_desc='units', fail_limit=None):
        if pool_ctxs is not None and len(pool_ctxs) != nworkers:
            return None
        self._avail_ctx = pool_ctxs

        nwrkrs = nworkers if nworkers > 0 else 1
        self._pool = futures.ThreadPoolExecutor(max_workers=nwrkrs)

        self._futures = []
        self._retry = retry if retry >= 0 else 0

        self._progress_bar = tqdm(total=pb_elts, desc=pb_desc, unit=pb_desc, unit_scale=True, mininterval=1.0) if pb_elts is not None else None
        self.fail_limit = fail_limit
        self.errors_count = 0

    def _retry_wait(self, retry):
        wait = 1 + 2 * random.randint(0, retry)
        log.debug(output_messages['DEBUG_WAIT_BEFORE_NEXT_ATTEMP'] % wait, class_name=POOL_CLASS_NAME)
        time.sleep(wait)

    def _submit_fn(self, userfn, *args, **kwds):
        ctx = self._get_ctx()

        result = False
        retry_cnt = 0
        while True:
            try:
                if ctx is not None:
                    result = userfn(ctx, *args, **kwds)
                else:
                    result = userfn(*args, **kwds)
            except Exception as e:
                if retry_cnt < self._retry:
                    retry_cnt += 1
                    log.debug(output_messages['WARN_WORKER_EXCEPTION'] % (e, retry_cnt), class_name=POOL_CLASS_NAME)
                    self._retry_wait(retry_cnt)
                    continue
                elif self.fail_limit is not None and self.errors_count >= self.fail_limit:
                    self.errors_count += 1
                    self.cancel()
                    raise e
                else:
                    self.errors_count += 1
                    self._progress_bar.set_postfix({'Failed': self.errors_count})
                    log.debug(output_messages['ERROR_WORKER_FAILURE'] % (e, retry_cnt), class_name=POOL_CLASS_NAME)
                    self._release_ctx(ctx)
                    raise e
            break

        log.debug(output_messages['DEBUG_WORKER_SUCESS'] % (retry_cnt+1), class_name=POOL_CLASS_NAME)
        self._release_ctx(ctx)
        self._progress()

        return result

    def submit(self, userfn, *args, **kwds):
        self._futures.append(self._pool.submit(self._submit_fn, userfn, *args, **kwds))

    def _get_ctx(self):
        if self._avail_ctx is not None:
            return self._avail_ctx.pop()

    def _release_ctx(self, ctx):
        if ctx is not None:
            self._avail_ctx.append(ctx)

    def progress_bar_total_inc(self, cnt):
        self._progress_bar.total += cnt

    def _progress(self, units=1):
        if self._progress_bar is not None:
            self._progress_bar.update(units)

    def progress_bar_close(self):
        self._progress_bar.close()

    def reset_futures(self):
        del(self._futures)
        self._futures = []

    def wait(self):
        futures.wait(self._futures)
        return self._futures

    def cancel(self):
        for thread in self._futures:
            thread.cancel()


def process_futures(futures_to_process, wp):
    for future in futures_to_process:
        future.result()
    wp.reset_futures()
