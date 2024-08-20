import numpy as np
import pandas as pd

def visibility(val, factor: float, limit: float):
    """factor between 0 and 1"""
    norm = np.abs(val / limit)
    b = 1.5 - factor * 0.1
    return np.where(norm > 1, norm, norm**b) * limit * np.sign(val)




if __name__=='__main__':
    import plotly.express as px


    x = np.linspace(0, 20, 100)
    px.line(pd.DataFrame({k: visibility(x, k, 10) for k in np.linspace(0.1,1,9)}, index=x)).show()

    x = np.linspace(0, 2, 100)
    px.line(pd.DataFrame({k: visibility(x, k, 1) for k in np.linspace(0.1,1,9)}, index=x)).show()