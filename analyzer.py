import numpy as np
import plotly.graph_objects as go

class IntegralAnalyzer:
    def __init__(self, cumulative, final_estimate, bounds, func):
        self.cumulative = np.asarray(cumulative, dtype=float)
        if np.isnan(self.cumulative).all():
            self.cumulative = np.array([0.0])
        self.final_estimate = float(final_estimate) if not np.isnan(final_estimate) else 0.0
        self.bounds = bounds
        self.func = func
        self.errors = np.abs(self.cumulative - self.final_estimate)

    @classmethod
    def from_agent(cls, agent, func, final_estimate):
        cumulative = getattr(agent, "cumulative_estimates", None)
        if cumulative is None or len(cumulative) == 0:
            cumulative = np.full(50, final_estimate if not np.isnan(final_estimate) else 0.0)
        return cls(cumulative, final_estimate, agent.bounds, func)

    def plot_convergence(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=self.cumulative, mode="lines", name="Estimate"))
        fig.add_hline(y=self.final_estimate, line_dash="dash", line_color="red", name="Final")
        fig.update_layout(title="Convergence of Integral Estimate", xaxis_title="Iteration", yaxis_title="Estimate")
        return fig

    def plot_absolute_error(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=self.errors, mode="lines", name="|Error|"))
        fig.update_layout(title="Absolute Error vs Iteration", yaxis_title="Absolute Error")
        return fig

    def plot_error_histogram(self):
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=self.errors, nbinsx=30))
        fig.update_layout(title="Error Distribution", xaxis_title="Absolute Error")
        return fig

    def summary(self):
        return {
            "mean_error": float(np.mean(self.errors)) if len(self.errors) > 0 else 0.0,
            "max_error": float(np.max(self.errors)) if len(self.errors) > 0 else 0.0,
            "min_error": float(np.min(self.errors)) if len(self.errors) > 0 else 0.0,
            "converged": bool(self.errors[-1] < (np.mean(self.errors) if len(self.errors) > 0 else 1e-6)),
        }

    def summarize(self, method, dimension, valid_ratio, final_estimate):
        base = self.summary()
        base.update({
            "method": method,
            "dimension": dimension,
            "valid_ratio": valid_ratio,
            "estimate": final_estimate,
        })
        return base