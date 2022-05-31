"""Hill equation fit for peak amplitiude x rstarr"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit

class WeberEquation:

	def __init__(self, beta = None):
		self.beta: float = beta
		self.r2: float = None
	
	def __call__(self, X):
		if self.beta is None:
			raise Exception("Fit Weber function first.")
		return self.equation(X, self.beta)

	def invequation(self, x):
		return self.beta * (1/x - 1)

	@property
	def ihalf(self):
		return self.invequation(0.5)

	def fit(self, X, Y, p0 = (-1,), **kwargs):
		# NORMALIZE FIT DATA
		X_, Y_ = self.normalize(X, Y)

		fit = curve_fit(self.equation, X_, Y_, p0 = p0, **kwargs)

		self.beta = fit[0][0]

		# CALCULATE RSQUARED
		residuals = Y_ - self(X_)
		ss_res = np.sum(residuals**2)
		ss_tot = np.sum((Y_ - np.mean(Y_))**2)
		self.r2 = 1 - (ss_res / ss_tot)

	@staticmethod
	def normalize(X,Y):
		indexes = list(range(len(X)))
		indexes.sort(key=X.__getitem__)

		X_ = X[indexes]
		Y_ = Y[indexes]
		Y_ = Y_ / Y_[0]
		return X_, Y_

	@staticmethod
	def equation(X, beta):
		return 1 / (1 + (X / beta))