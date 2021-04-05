import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

with st.echo(code_location='below'):
    st.title("Hello, World!!!!!")
    """
    This is a test.
    """
    x = np.linspace(0, 10, 500)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    plt.ylim(-2, 2)
    st.pyplot(fig)

    data = pd.read_csv('https://github.com/ryakina/Airbnb_NY/blob/main/AB_NYC_2019.csv')
    data.hist()
    plt.show()
