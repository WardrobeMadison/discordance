import plotly.express as px
import numpy as np
import pandas as pd


X = np.random.randn(20000)
Y = 2 * X ** 4 - 3*X**2

df = pd.DataFrame(columns = "X Y".split(), data = zip(X, Y))


px.scatter(
    df,
    x = "X", y = "Y"
)