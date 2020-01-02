import matplotlib.pyplot as plt
import matplotlib.patches as patches

twitter_color = '#841d26'
COLOR = 'white'

XMAX, XMIN = 120, 0
YMAX, YMIN = 80, 0

def draw_pitches(nrows, ncols, colorbar=False):
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