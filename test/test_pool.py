"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.pool import WorkerPool

import unittest

class Context(object):
	def __init__(self, i):
		self._i = i

	def __repr__(self):
		return "context: %s" % str(self._i)

nexc = 0
def job_no_ctx(abc, bcd, exc=False):
	global nexc
	print("nexc : %d %s" % (nexc, exc))
	if exc == True and nexc < 2:
		print("nexc : %d %s" % (nexc, exc))
		nexc += 1
		raise Exception("worker pool exception")
	return abc * bcd

def job_with_ctx(ctx, abc, bcd):
	abcd = job_no_ctx(abc, bcd)
	return "%s %d" % (ctx, abcd)

class PoolTestCases(unittest.TestCase):
	def test_single_job_wrong_nworkers(self):
		wp = WorkerPool(nworkers=0)

		wp.submit(job_no_ctx, 10, 10)

		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertEqual(fut.result(), job_no_ctx(10, 10))

	def test_single_job(self):
		wp = WorkerPool(nworkers=1)

		wp.submit(job_no_ctx, 10, 10)

		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertEqual(fut.result(), job_no_ctx(10, 10))

	def test_single_job_with_exception(self):
		wp = WorkerPool(nworkers=1)

		wp.submit(job_no_ctx, 10, 10, True)

		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertRaises(Exception, fut.result)

	def test_single_job_with_exception_and_retry(self):
		global nexc
		nexc = 0

		wp = WorkerPool(nworkers=1, retry=2)

		wp.submit(job_no_ctx, 10, 10, True)

		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertEqual(fut.result(), job_no_ctx(10, 10))

	def test_single_job_with_exception_and_failed_retry(self):
		global nexc
		nexc = 0

		wp = WorkerPool(nworkers=1, retry=1)

		wp.submit(job_no_ctx, 10, 10, True)

		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertRaises(Exception, fut.result)

	def test_single_job_with_ctx(self):
		ctx = Context(1)
		ctxs = [ ctx ]
		wp = WorkerPool(nworkers=1, pool_ctxs=ctxs)

		wp.submit(job_with_ctx, 10, 10)
		futs = wp.wait()
		self.assertEqual(len(futs), 1)
		for fut in futs:
			self.assertEqual(fut.result(), job_with_ctx(ctxs[0], 10, 10))

	def test_multiple_jobs(self):
		njobs = 10

		wp = WorkerPool(nworkers=10)
		for i in range(njobs):
			wp.submit(job_no_ctx, 10*i, 10*i)

		futs = wp.wait()
		self.assertEqual(len(futs), njobs)
		for i in range(njobs):
			self.assertEqual(futs[i].result(), job_no_ctx(10*i, 10*i))

	def test_multiple_jobs_with_less_workers(self):
		njobs = 10

		wp = WorkerPool(nworkers=5)
		for i in range(njobs):
			wp.submit(job_no_ctx, 10*i, 10*i)

		futs = wp.wait()
		self.assertEqual(len(futs), njobs)
		for i in range(njobs):
			self.assertEqual(futs[i].result(), job_no_ctx(10*i, 10*i))