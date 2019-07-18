"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
import concurrent.futures
from tqdm import tqdm

class WorkerPool(object):
	def __init__(self, nworkers=10, pool_ctxs=None, pb_elts=None, pb_desc="units"):
		if pool_ctxs is not None and len(pool_ctxs) != nworkers: return None
		self._free_ctx = pool_ctxs

		self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=nworkers)
		self._progress_bar = tqdm(total=pb_elts, desc=pb_desc, unit=pb_desc, unit_scale=True, mininterval=1.0)
		self._futures = []

	def _submit_fn(self, userfn, *args):
		try:
			ctx = self._getctx() if self._free_ctx is not None else None
			result = userfn(ctx, *args)
			self._freectx(ctx) if ctx is not None else None

			self._progress() if self._progress_bar is not None else None
		except Exception as e:
			log.error("WorkerPool: exception -- [%s]" % (e))
			raise(e)

		return result

	def submit(self, userfn, *args):
		self._futures.append(self._pool.submit(self._submit_fn, userfn, *args))

	def _getctx(self):
		return self._free_ctx.pop()

	def _freectx(self, ctx):
		self._free_ctx.append(ctx)

	def _progress(self, units=1):
		self._progress_bar.update(units)

	def wait(self):
		concurrent.futures.wait(self._futures)


if __name__=="__main__":
	class Context(object):
		def __init__(self, i):
			self._i = i

		def __repr__(self):
			return "context: %s" % str(self._i)

	def fn(ctx, abc, bcd):
		try:
			import time
			import random
			# fail = random.randint(0, 1000)
			# if fail > 700: raise Exception("bla bla bla")

			# attempt to do something useful with my cpu cycles :)
			time.sleep(float(random.randrange(1, 10)) / 100)
			# print("%s -> %s" % (abc, ctx))
		except Exception as e:
			print(e)

	nworkers = 10
	njobs = nworkers*100
	ctxs = [ Context(i) for i in range(nworkers) ]
	wp = WorkerPool(nworkers, ctxs, njobs)

	for i in range(njobs):
		abc = "fn %d" % (i)
		wp.submit(fn, abc, abc)
	wp.wait()