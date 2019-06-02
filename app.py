

import pandas as pd
#import matplotlib.pyplot as plt

import dash
#import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#import savings
#from savings import calculate_savings, gr_monthly


def gr_monthly(ann_gr):
    return((1+(ann_gr/100))**(1/12))


def calculate_savings(initial_value, goal, savings_pm, \
    withdraw_pm, rtn, current_age, supplement_cash, \
    retire_age = 67, inf_adj=2, adj=False):
    
    growth_rate = gr_monthly(rtn)
    inf_adj_rate = gr_monthly(inf_adj)
    tmp_v = initial_value
    months = 1
    age_threshold = retire_age-current_age
    savings = initial_value
    goal_adj = goal
    shortfall = goal - tmp_v

    tmp_ls = [[months, initial_value, savings_pm, rtn, goal, shortfall, goal_adj,\
    savings, current_age, 0]]

    while months/12 < age_threshold:
        months+=1
        tmp_v = tmp_v*growth_rate+savings_pm
        savings += savings_pm
        years = months/12
        if adj:
            shortfall = goal_adj - tmp_v
        else:
            shortfall = goal - tmp_v

        tmp_ls.append([months, tmp_v, savings_pm, rtn, goal, \
            shortfall, goal_adj, savings, current_age + years, years])
    cols = {0: "Month_Num", 1:"Value", 2:"Regular_Saving", 3:"Ann_Rate", \
    4:"Goal", 5:"Shortfall", 6:"Goal_Inf_Adjusted", 7:"Total_Savings", \
    8:"Age", 9:"Years"}

    
    list_len = len(tmp_ls)-1
    v_max_value = tmp_ls[list_len][1]
    v_max_value += supplement_cash
    v_years = tmp_ls[list_len][9]
    v_age = tmp_ls[list_len][8]
    v_months = tmp_ls[list_len][0]
    

    #tmp_ls = []
    months = 0
    all_money = v_max_value

    if adj:
        base_withdraw_pm = withdraw_pm * ((1+inf_adj/100))**(v_months/12)

    while all_money > 0:
        months+=1
        if adj:
            withdraw_pm = base_withdraw_pm * ((1+inf_adj/100))**(months/12)

        all_money -= withdraw_pm
        tmp_ls.append([months, all_money, -withdraw_pm, 0, None, None, None, \
            None, v_age + months/12, years + months/12])

    df_tmp = pd.DataFrame(tmp_ls)
    df_tmp = df_tmp.rename(columns = cols)
    print("Age when broke: ", df_tmp.iloc[-1]['Age'])

    return(df_tmp)




app = dash.Dash(__name__)



#VALID_USERNAME_PASSWORD_PAIRS = ['ben','edwards']

#auth = dash_auth.BasicAuth(
#    app,
#    VALID_USERNAME_PASSWORD_PAIRS
#)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Objective Orientated Savings'),

    html.Div(children='''
        OOS: A visual of the impact of saving & compound interest! 
        
        Please update the below accordingly:
    '''),
    
    html.Div(id='output-keypress-1'),
    dcc.Input(id = 'V_VALUE_TODAY', value=10000, type='number') ,
    html.Div(id='output-keypress-2'),
    dcc.Input(id = 'V_REG_SAVE_PM', value=100, type='number') ,
    html.Div(id='output-keypress-3'),
    dcc.Input(id = 'V_WITHDRAWAL_PM', value=1200, type='number') ,
    html.Div(id='output-keypress-4'),
    dcc.Input(id = 'V_AGE', value=30, type='number') ,
    html.Div(id='output-keypress-5'),
    dcc.Input(id = 'V_SUPPLEMENT', value=10000, type='number') ,
    html.Div(id='output-keypress-6'),
    dcc.Input(id = 'V_RETIREMENT_AGE', value=69, type='number') ,
    html.Div(id='output-keypress-7'),
    dcc.Input(id = 'V_INF_ADJ', value='Yes', type='string') ,

    html.Div(id='my-div'),
    
    dcc.Graph(
        id='example-graph'
    )
])

@app.callback(Output('output-keypress-1', 'children'),
              [Input('V_VALUE_TODAY', 'value')])
def update_output(V_VALUE_TODAY):
    return u'Current value of investments: "£{:0,.0f}" '.format(V_VALUE_TODAY)

@app.callback(Output('output-keypress-2', 'children'),
              [Input('V_REG_SAVE_PM', 'value')])
def update_output(V_REG_SAVE_PM):
    return u'Monthly savings into pension: "£{:0,.0f}" '.format(V_REG_SAVE_PM)

@app.callback(Output('output-keypress-3', 'children'),
              [Input('V_WITHDRAWAL_PM', 'value')])
def update_output(V_WITHDRAWAL_PM):
    return u'Monthly withdrawals in drawdown/retirement: "£{:0,.0f}" per month or "£{:0,.0f}" per year'.format(V_WITHDRAWAL_PM, V_WITHDRAWAL_PM*12)

@app.callback(Output('output-keypress-4', 'children'),
              [Input('V_AGE', 'value')])
def update_output(V_AGE):
    return u'Current age is: "{}" '.format(V_AGE)

@app.callback(Output('output-keypress-5', 'children'),
              [Input('V_SUPPLEMENT', 'value')])
def update_output(V_SUPPLEMENT):
    return u'Any other investment available at retirement: "£{:0,.0f}" '.format(V_SUPPLEMENT)

@app.callback(Output('output-keypress-6', 'children'),
              [Input('V_RETIREMENT_AGE', 'value')])
def update_output(V_RETIREMENT_AGE):
    return u'Age you would like to retire: "{}" '.format(V_RETIREMENT_AGE)

@app.callback(Output('output-keypress-7', 'children'),
              [Input('V_INF_ADJ', 'value')])
def update_output(V_INF_ADJ):
    return u'If you want to adjust for inflation @2%, please select yes here: '


@app.callback(
Output(component_id = 'example-graph', component_property='figure'),
    [Input(component_id = 'V_VALUE_TODAY', component_property='value'),
    Input(component_id = 'V_REG_SAVE_PM', component_property='value'),
    Input(component_id = 'V_WITHDRAWAL_PM', component_property='value'),
    Input(component_id = 'V_AGE', component_property='value'),
    Input(component_id = 'V_SUPPLEMENT', component_property='value'),
    Input(component_id = 'V_RETIREMENT_AGE', component_property='value'),
    Input(component_id = 'V_INF_ADJ', component_property='value'),
    ]
)
def update_output(V_VALUE_TODAY, V_REG_SAVE_PM, V_WITHDRAWAL_PM, \
                  V_AGE, V_SUPPLEMENT, V_RETIREMENT_AGE ,V_INF_ADJ):
    
    if V_INF_ADJ.lower() == 'yes':
        V_INF_ADJ = True
    else:
        V_INF_ADJ = False

    V_GOAL = 400000    
    V_INFLATION = float(2.0)
    
    df_low_risk = calculate_savings(V_VALUE_TODAY, V_GOAL, V_REG_SAVE_PM, V_WITHDRAWAL_PM, \
        3.0, V_AGE, V_SUPPLEMENT, V_RETIREMENT_AGE, V_INFLATION, V_INF_ADJ)

    df_med_risk = calculate_savings(V_VALUE_TODAY, V_GOAL, V_REG_SAVE_PM, V_WITHDRAWAL_PM, \
        5.0, V_AGE, V_SUPPLEMENT, V_RETIREMENT_AGE, V_INFLATION, V_INF_ADJ)

    df_high_risk = calculate_savings(V_VALUE_TODAY, V_GOAL, V_REG_SAVE_PM, V_WITHDRAWAL_PM, \
        7.0, V_AGE, V_SUPPLEMENT, V_RETIREMENT_AGE, V_INFLATION, V_INF_ADJ)
    
    return({'data': [
                {'x': df_low_risk.Age.tolist(), 'y': df_low_risk.Value.tolist(), 'type': 'line', 'name': 'Low Risk - 3%'},
                {'x': df_med_risk.Age.tolist(), 'y': df_med_risk.Value.tolist(), 'type': 'line', 'name': u'Medium Risk - 5%'},
                {'x': df_high_risk.Age.tolist(), 'y': df_high_risk.Value.tolist(), 'type': 'line', 'name': u'High Risk - 7%'},
            ],
            'layout': {
                'title': 'Savings Horizon'}
           })

if __name__ == '__main__':
    app.run_server(debug=False)
    

    
