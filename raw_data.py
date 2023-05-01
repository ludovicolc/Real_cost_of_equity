import pandas as pd
import streamlit as st

class Data:
    def __init__(self):
        self.__df_ke = self.get_data()
        self.__calculate_ker()
        self.__history()
    
    def __calculate_ker(self):            
        # real cost of equity
        self.erp_current = round(self.__df_ke['erp'][0] * 100, 2)
        self.ker_current = round(self.__df_ke['Ker'][0] * 100, 2)
        self.ker_mean = round(self.__df_ke['Ker'].mean() * 100, 2)
        self.ker_delta = round((self.__df_ke['Ker'][0] / self.__df_ke['Ker'][1] -1) * 100, 2)

        # cost of equity (TIPS)
        self.ke_tips_current = round(self.__df_ke['tips'][0] * 100, 2)
        self.ke_tips_spread_current = round(self.__df_ke['Ke_tips_spread'][0] * 100, 2)
        self.ke_tips_spread_mean = round(self.__df_ke['Ke_tips_spread'].mean() * 100, 2)
        self.ke_tips_spread_delta = round((self.__df_ke['Ke_tips_spread'][0] / self.__df_ke['Ke_tips_spread'][1] -1) * 100, 2)

        # cost of equity (expected inflation)
        self.ke_exp_inflation_current = round(self.__df_ke['Ke_exp_inflation'][0] * 100, 2)
        self.ke_exp_inflation_mean = round(self.__df_ke['Ke_exp_inflation'].mean() * 100, 2)
        self.ke_exp_inflation_delta = round((self.__df_ke['Ke_exp_inflation'][0] / self.__df_ke['Ke_exp_inflation'][1] -1) * 100, 2)
        
        return self
    
    def __history(self):
        self.hist = self.__df_ke[['Date', 'tips', 'erp']].loc[1:20]
        self.minimum = int(self.__df_ke['Date'][20])
        self.maximum = int(self.__df_ke['Date'][1])
        return self
    
    @st.cache_data
    def get_data():
        # pe
        pe = pd.read_html('https://www.multpl.com/s-p-500-pe-ratio/table/by-year')
        df_pe = pd.DataFrame(pe[0])
        df_pe['Value Value'] = df_pe['Value Value'].str.replace('estimate', '')
        df_pe['Value Value'] = pd.to_numeric(df_pe['Value Value'])
        df_pe.rename(columns = {'Value Value':'Pe'}, inplace = True)

        # earning yield %
        ey = pd.read_html('https://www.multpl.com/s-p-500-earnings-yield/table/by-year')
        df_ey = pd.DataFrame(ey[0])
        df_ey['Value Value'] = df_ey['Value Value'].str.replace('%', '')
        df_ey['Value Value'] = df_ey['Value Value'].str.replace('estimate', '')
        df_ey['Value Value'] = pd.to_numeric(df_ey['Value Value']) / 100
        df_ey.rename(columns = {'Value Value':'Earning_y'}, inplace = True)

        # price to book value
        pb = pd.read_html('https://www.multpl.com/s-p-500-price-to-book/table/by-year')
        df_pb = pd.DataFrame(pb[0])
        df_pb['Value Value'] = df_pb['Value Value'].str.replace('%', '')
        df_pb['Value Value'] = df_pb['Value Value'].str.replace('estimate', '')
        df_pb['Value Value'] = pd.to_numeric(df_pb['Value Value'])
        df_pb.rename(columns = {'Value Value':'Price_book'}, inplace = True)

        # US real GDP growth %
        gr = pd.read_html('https://www.multpl.com/us-real-gdp-growth-rate/table/by-year')
        df_gr = pd.DataFrame(gr[0])
        df_gr['Value Value'] = df_gr['Value Value'].str.replace('%', '')
        df_gr['Value Value'] = df_gr['Value Value'].str.replace('estimate', '')
        df_gr['Value Value'] = pd.to_numeric(df_gr['Value Value']) / 100
        df_gr.rename(columns = {'Value Value':'real_gdp'}, inplace = True)

        # US inflation
        infl = pd.read_html('https://www.multpl.com/inflation/table/by-year')
        df_infl = pd.DataFrame(infl[0])
        df_infl['Value Value'] = df_infl['Value Value'].str.replace('%', '')
        df_infl['Value Value'] = df_infl['Value Value'].str.replace('estimate', '')
        df_infl['Value Value'] = pd.to_numeric(df_infl['Value Value']) / 100
        df_infl.rename(columns = {'Value Value':'inflazione'}, inplace = True)

        # 10 yr interest rate
        ir = pd.read_html('https://www.multpl.com/10-year-treasury-rate/table/by-year')
        df_ir = pd.DataFrame(ir[0])
        df_ir['Value Value'] = df_ir['Value Value'].str.replace('%', '')
        df_ir['Value Value'] = pd.to_numeric(df_ir['Value Value']) / 100
        df_ir.rename(columns = {'Value Value':'interest_rate'}, inplace = True)

        # 10 yr real interest rate TIPS
        tips = pd.read_html('https://www.multpl.com/10-year-real-interest-rate/table/by-year')
        df_tips = pd.DataFrame(tips[0])
        df_tips['Value Value'] = df_tips['Value Value'].str.replace('%', '')
        df_tips['Value Value'] = pd.to_numeric(df_tips['Value Value']) / 100
        df_tips.rename(columns = {'Value Value':'tips'}, inplace = True)

        # df ensamble
        df_pe['price_book'] = df_pb['Price_book']
        df_pe['earning_y'] = df_ey['Earning_y']
        df_pe['real_gdp'] = df_gr['real_gdp']
        df_pe['inflazione'] = df_infl['inflazione']
        df_pe['Roe'] = df_pe['price_book'] / df_pe['Pe']
        df_pe['interest_rate'] = df_ir['interest_rate']
        df_pe['tips'] = df_tips['tips']

        # intermediary df
        inter_df = df_pe.head(24)
        
        # final df
        df_ke = pd.DataFrame(columns = ['Date', 'earning_yield', 'g', 'Roe', 'gr', 'expected_inflation', 'interest_rate', 'tips', 'tips_spread'])
        df_ke['Date'] = inter_df['Date']
        df_ke['earning_yield'] = inter_df['earning_y']
        df_ke['tips'] = inter_df['tips']
        df_ke['interest_rate'] = inter_df['interest_rate']

        # adjustments
        for x in df_ke['Roe']:
            df_ke['Roe'] = inter_df['Roe'].mean()

        for x in df_ke['gr']:
            df_ke['gr'] = inter_df['real_gdp'].mean()

        # expected inflation
        expected_infl = []
        t_period = 0
        for x in inter_df['inflazione']:
            inflation = (inter_df.iloc[(0 + t_period):(5 + t_period)]['inflazione'].mean())
            t_period = t_period + 1
            expected_infl.append(inflation)
        df_ke['expected_inflation'] = expected_infl

        # between values operations
        df_ke['g'] = df_ke['gr'] + df_ke['expected_inflation']
        df_ke['tips_spread'] = df_ke['interest_rate'] - df_ke['tips']
        df_ke['Ker'] = df_ke['earning_yield'] * (1 - (df_ke['g'] / df_ke['Roe'])) + df_ke['gr']

        # inflation adjusted erp
        df_ke['erp'] = df_ke['Ker'] - df_ke['tips']
        
        # Ke (expected inflation)
        df_ke['Ke_exp_inflation'] = df_ke['Ker'] + df_ke['expected_inflation']
        
        # Ke (tips spread)
        df_ke['Ke_tips_spread'] = df_ke['Ker'] + df_ke['tips_spread']
        
        # inflation adjusted erp
        df_ke['erp'] = df_ke['Ker'] - df_ke['tips']

        # date conversion
        d = 0
        for x in df_ke['Date']:
            df_ke['Date'][d] = df_ke['Date'][d].replace(x, x[-4:])
            d = d + 1
        df_ke['Date'] = pd.to_numeric(df_ke['Date'])
        
        return df_ke