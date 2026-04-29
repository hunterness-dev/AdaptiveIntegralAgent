import numpy as np

class AdaptiveIntegralAgent:
    def __init__(self, bounds, n_samples=3000):
        self.bounds = bounds
        self.n_samples = n_samples
        self.stats = {}
        self.samples = None
        self.cumulative_estimates = None

    def integrate(self, func, expr=None):
        n_dim = len(self.bounds)

        self.samples = np.random.rand(self.n_samples, n_dim)
        for i, (a, b) in enumerate(self.bounds):
            self.samples[:, i] = self.samples[:, i] * (b - a) + a

        values = np.array([func(s) for s in self.samples])
        mask = np.isfinite(values)

        valid_ratio = np.sum(mask) / len(values)
        self.stats["valid_ratio"] = valid_ratio

        if not np.any(mask):
            self.cumulative_estimates = np.array([np.nan])
            return np.nan, "Monte Carlo", self.cumulative_estimates

        self.cumulative_estimates = (
            np.cumsum(values[mask]) / np.arange(1, np.sum(mask) + 1)
        )
        result = np.mean(values[mask])
        method = "Monte Carlo"

        return result, method, self.cumulative_estimates