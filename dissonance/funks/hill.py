"""Hill equation fit for peak amplitiude x rstarr"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit

def hillequation(x, expnt, base, rmax, xhalf): 
	return base + (rmax - base) / (1 + (xhalf/x)**expnt) 

def invhillequation(y, expnt, base, rmax, xhalf):
	return xhalf / ((rmax - base) / (y-base) - 1) ** 1 / expnt

@dataclass
class HillParams:
	expnt: float
	base: float
	rmax: float
	xhalf: float
	ihalf: float
	r2: float
	
	def __call__(self, x):
		return hillequation(
			x, self.expnt, self.base, self.rmax, self.xhalf)

def fit(X, Y) -> HillParams:
	bounds = (0.0, np.inf)
	fit = curve_fit(hillequation, 
		xdata = X, ydata= Y, maxfev=10000,
		p0 = [1.0, 10, 150, 0.5], bounds = bounds)
	popt = fit[0]

	#You can get the residual sum of squares (ss_tot) with
	residuals = Y- hillequation(X, *popt)
	ss_res = np.sum(residuals**2)

	#You can get the total sum of squares (ss_tot) with
	ss_tot = np.sum((Y-np.mean(Y))**2)

	#And finally, the r_squared-value with,
	ihalf = invhillequation(max(Y)/2, *popt)

	r_squared = 1 - (ss_res / ss_tot)

	return HillParams(*popt, ihalf, r_squared)