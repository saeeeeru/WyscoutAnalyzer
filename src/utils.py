import matplotlib.pyplot as plt
import matplotlib.patches as patches

import plotly.graph_objs as go
import plotly.express as px

from plotly.subplots import make_subplots

COLOR = 'white'

XMAX, XMIN = 120, 0
YMAX, YMIN = 80, 0

def draw_pitches_matplotlib(nrows, ncols, colorbar=False):
    twitter_color = '#841d26'
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10*ncols, 8*nrows if colorbar else 7*nrows), facecolor=twitter_color)
    
    fig.patch.set_facecolor('#141d26')
    
    for ax in axes.flatten():
        ax.patch.set_facecolor('#141d26')
        
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        

        ax.plot([0,120], [0, 0], color=COLOR)
        ax.plot([120,120], [0, 80], color=COLOR)
        ax.plot([120,0], [80,80], color=COLOR)
        ax.plot([0, 0], [80, 0], color=COLOR)
        ax.plot([60, 60], [0, 80], color=COLOR)
        ax.plot([0, 0], [36, 44], color=COLOR, linewidth=10)
        ax.plot([120, 120], [36, 44], color=COLOR, linewidth=10)

        centreCircle = plt.Circle((60, 40), 12, color=COLOR, fill=False)
        ax.add_patch(centreCircle)

        ax.plot([0, 18],  [18, 18], color=COLOR)
        ax.plot([18, 18],  [18, 62], color=COLOR)
        ax.plot([18, 0],  [62, 62], color=COLOR)
        ax.plot([0, 6],  [30, 30], color=COLOR)
        ax.plot([6, 6],  [30, 50], color=COLOR)
        ax.plot([6, 0],  [50, 50], color=COLOR)

        ax.plot([120, 102],  [18, 18], color=COLOR)
        ax.plot([102, 102],  [18, 62], color=COLOR)
        ax.plot([102, 120],  [62, 62], color=COLOR)
        ax.plot([120, 114],  [30, 30], color=COLOR)
        ax.plot([114, 114],  [30, 50], color=COLOR)
        ax.plot([114, 120],  [50, 50], color=COLOR)

        ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

    return fig, axes

def draw_pitches_plotly(nrows, ncols, title_list=[], colorbar=False):
    twitter_color = 'rgb(20,29,38)'

    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=title_list, horizontal_spacing=0.05, vertical_spacing=0.05)
    for i in range(1,nrows+1):
        for j in range(1,ncols+1):
            
            line_list = [[[0,120], [0,0]], [[120,120], [0,80]], [[120,0], [80,80]], [[0,0], [80,0]], [[60,60], [0,80]]]
            line_list += [[[0,18], [18,18]], [[18,18], [18,62]], [[18,0], [62,62]], [[0,6], [30,30]], [[6,6], [30,50]], [[6,0], [50,50]]]
            line_list += [[[120, 102], [18,18]], [[102,102], [18,62]], [[102,120], [62,62]], [[120,114], [30,30]], [[114,114], [30,50]], [[114,120], [50,50]]]

            for [x, y] in line_list:
                fig.add_trace(go.Scatter(x=x, y=y,
                                    mode='lines',
                                    line=dict(color=COLOR, width=2.5),
                                    showlegend=False,
                                    hoverinfo='none'
                                    )
                             , row=i, col=j)

            line_list = [[[0,0], [36,44]], [[120,120], [36,44]]]
            for [x, y] in line_list:
                fig.add_trace(go.Scatter(x=x, y=y,
                                    mode='lines',
                                    line=dict(color=COLOR, width=12.5),
                                    showlegend=False,
                                    hoverinfo='none'
                                    )
                             , row=i, col=j)

            fig.add_shape(go.layout.Shape(type='circle', x0=60-12, y0=40-12, x1=60+12, y1=40+12, line_color=COLOR, line_width=2.5), row=i, col=j)
            fig.update_xaxes(range=[-1, 120+1], visible=False, row=i, col=j)
            fig.update_yaxes(range=[-1, 80+1], visible=False, row=i, col=j)
    
    fig.update_layout(go.Layout(width=120*10*(ncols/2), height=80*10*(nrows/2), plot_bgcolor=twitter_color, paper_bgcolor=twitter_color, autosize=True, margin=dict(l=10, r=10, t=20, b=10), legend=dict(font=dict(color=COLOR))))
    
    for i in fig['layout']['annotations']:
        i['font'] = dict(size=15,color=COLOR)
    
    return fig