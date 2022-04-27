"""Hill equation fit for peak amplitiude x rstarr"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit


class HillEquation:

    def __init__(self,
                 expnt: float = None,
                 base: float = None,
                 rmax: float = None,
                 xhalf: float = None):

        self.expnt: float = expnt
        self.base: float = base
        self.rmax: float = rmax
        self.xhalf: float = xhalf
        self.ihalf: float = None
        self.r2: float = None

    def __call__(self, x):
        if not self.hasparams:
            raise Exception("Fit Hill function first or provide parameters.")

        return self.equation(
            x, self.expnt, self.base, self.rmax, self.xhalf)

    def fit(self, X, Y, bounds = (0.0, np.inf), maxfev=20000, **kwargs):
        p0 = [2.0, np.mean(Y), max(Y), 0.5]
        fit = curve_fit(self.equation,
                        xdata=X, ydata=Y, 
						maxfev=maxfev, p0=p0, bounds=bounds, 
						**kwargs)
        self.expnt, self.base, self.rmax, self.xhalf = fit[0]

        # You can get the residual sum of squares (ss_tot) with
        # You can get the total sum of squares (ss_tot) with
        residuals = Y - self(X)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((Y-np.mean(Y))**2)
        self.r2 = 1 - (ss_res / ss_tot)

        self.ihalf = self.invequation(max(Y)/2, *fit[0])
        # return HillParams(*popt, ihalf, r_squared)

    @property
    def hasparams(self):
        return not any(map(lambda x: x is None, [self.expnt, self.base, self.rmax, self.xhalf]))

    @staticmethod
    def equation(X, expnt, base, rmax, xhalf):
        return base + (rmax - base) / (1 + (xhalf/X)**expnt)

    @staticmethod
    def invequation(Y, expnt, base, rmax, xhalf):
        return xhalf / ((rmax - base) / (Y-base) - 1) ** 1 / expnt
