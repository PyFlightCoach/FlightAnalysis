import numpy as np
import pandas as pd


def visibility(val, factor: float, limit: float, kind: str = 'value'):
    """factor between 0 and 1"""

    b = 1.8 - factor * 0.8
    if kind == 'value':
        norm = np.abs(val / limit)
        return np.where(norm > 1, norm, norm**b) * limit * np.sign(val)
    elif kind=='deviation':
        diff = np.insert(np.diff(val), 0, 0.0, axis=0)
        norm = np.abs(diff / limit)

        res = np.where(norm > 1, norm, norm**b) * limit * np.sign(diff) 
        return res.cumsum() + val[0]
    else:
        raise ValueError(f'kind {kind} not recognized')



if __name__=='__main__':
    import plotly.express as px


    x = np.linspace(0, 20, 100)
    px.line(pd.DataFrame({k: visibility(x, k, 10) for k in np.linspace(0.1,1,9)}, index=x)).show()

    x = np.linspace(0, 2, 100)
    px.line(pd.DataFrame({k: visibility(x, k, 1) for k in np.linspace(0.1,1,9)}, index=x)).show()