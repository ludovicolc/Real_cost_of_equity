import streamlit as st
import pandas as pd
from company import Company_info
from raw_data import Data

# Page architecture
header = st.container()

# S&P 500 tickers
tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

# Collecting company information
@st.cache_resource
def loading_company_information(ticker):
    company = Company_info(ticker)
    return company

with header:
    st.title('Bottom Up Beta')
    tick_a = st.selectbox(label='Select principal company', options=tickers.Symbol.values)
    company_a = loading_company_information(tick_a)
    
    # Company information
    st.write(f'Name of the company: {company_a.name}')
    st.write(f'Industry: {company_a.industry}')
    st.write(f'Regression Beta: {round(company_a.beta, 2)}')
    
    st.subheader('Similar companies')
    
    # ticker symbol
    tick_b = st.selectbox(label='Select new company', options=tickers.Symbol.values)
    company_b = loading_company_information(tick_b)
    
    # Add company
    def insert_company():
        st.session_state.name.append(company_b.name)
        st.session_state.reg_beta.append(company_b.beta)
        st.session_state.debt_equity_ratio.append(company_b.debt_equity)
        st.session_state.tax_rate.append(company_b.mean_tax_rate)
        st.session_state.unlevered_beta.append(company_b.unlevered_beta)
        
    insert = st.button('Insert new company', on_click=insert_company)
    
    # Table
    if 'name' not in st.session_state:
        st.session_state.name = []
    if 'reg_beta' not in st.session_state:
        st.session_state.reg_beta = []
    if 'debt_equity_ratio' not in st.session_state:
        st.session_state.debt_equity_ratio = []
    if 'tax_rate' not in st.session_state:
        st.session_state.tax_rate = []
    if 'unlevered_beta' not in st.session_state:
        st.session_state.unlevered_beta = []
    
    df = pd.DataFrame({
            'Company name': st.session_state.name,
            'Regression Beta': st.session_state.reg_beta,
            'Debt equity ratio': st.session_state.debt_equity_ratio,
            'Tax rate': st.session_state.tax_rate,
            'Unlevered Beta': st.session_state.unlevered_beta
            })

    hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    tabella = st.table(df)

# Button to calculate levered beta
lev_beta = st.button('Calculate Levered Beta & Cost of equity')
if lev_beta:
    company_a_levered_beta = company_a.calculate_levered_beta(df['Unlevered Beta'].values)
    st.subheader(f'''{company_a.name} Levered Beta: {company_a_levered_beta}''')
    st.markdown("""---""")
    # Cost of equity
    st.title('Cost of equity')
    data = Data()
    ker_company = (data.erp_current/100 * company_a_levered_beta) + data.ke_tips_current/100
    ke_company_tips_spread = ker_company + data.ke_tips_spread_current/100
    ke_company_expected_inflation = ker_company + data.ke_exp_inflation_current/100
    
    col_1, col_2, col_3 = st.columns(3)
    col_1.metric('Real Cost of equity', f'{round(ker_company*100, 2)}%')
    col_2.metric('Cost of equity (TIPS spread)', f'{round(ke_company_tips_spread*100, 2)}%')
    col_3.metric('Cost of equity (Expected inflation)', f'{round(ke_company_expected_inflation*100, 2)}%')
    
else:
    st.subheader(f'''{company_a.name} Levered Beta: N/A''')