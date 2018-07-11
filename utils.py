import matplotlib.pyplot as plt
import seaborn as sns

def comparison_chart(first,second,first_label=None,second_label=None):
    sns.set_style('dark')
    fig=plt.figure(figsize=(14,10))
    ax=fig.add_subplot(111, label=first_label)
    ax2=fig.add_subplot(111, label=second_label, frame_on=False)

    ax.plot(first, color="C0")
    ax.set_xlabel(first_label, color="C0")
    ax.set_ylabel(first_label, color="C0")
    ax.tick_params(axis='x', colors="C0")
    ax.tick_params(axis='y', colors="C0")

    ax2.plot(second, color="white")
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    ax2.set_xlabel(second_label, color="gray") 
    ax2.set_ylabel(second_label, color="gray")       
    ax2.xaxis.set_label_position('top') 
    ax2.yaxis.set_label_position('right') 
    ax2.tick_params(axis='x', colors="gray")
    ax2.tick_params(axis='y', colors="gray")
    plt.show()
    return fig