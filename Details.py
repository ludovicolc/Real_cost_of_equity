import streamlit as st
import pandas as pd
from raw_data import Data

# principal data
data = Data()

# page architecture
header = st.container()
chart = st.container()
ticker_co = st.container()

# cost of equity (current & mean)
with header:
    st.title('S&P 500 Cost of equity')
    
    st.subheader('Current')
    col_x, col_y, col_z = st.columns(3)
    
    st.subheader('Mean')
    col_d, col_e, col_f = st.columns(3)
    
    col_x.metric('Real', f'{data.ker_current}%', f'{data.ker_delta}%')
    col_y.metric('TIPS spread', f'{data.ke_tips_spread_current}%', f'{data.ke_tips_spread_delta}%')
    col_z.metric('Expected inflation', f'{data.ke_exp_inflation_current}%', f'{data.ke_exp_inflation_delta}%')
    
    col_d.metric('Real', f'{data.ker_mean}%')
    col_e.metric('TIPS spread', f'{data.ke_tips_spread_mean}%')
    col_f.metric('Expected inflation', f'{data.ke_exp_inflation_mean}%')

    st.markdown("""---""")

# cost of equity (history)
with chart:
    st.header('Historical implied real cost of equity')
    
    col1, col2, col3 = st.columns(3)
    
    minimum = data.minimum
    maximum = data.maximum
    slides = col1.slider('', min_value=minimum, max_value=maximum, value=(minimum, maximum))

    # real cost of equity (breakdown)
    stack_ker = data.hist
    stack_ker.rename(columns={'tips': 'TIPS', 'erp': 'ERP'}, inplace=True)
    stack_ker.set_index('Date', inplace = True)
    st.bar_chart(stack_ker.loc[slides[1]:slides[0]])