import os
import sys
import pandas
import numpy as np
import matplotlib.pyplot as plt


if __name__=='__main__':

    filedir = os.path.abspath('../data')
    filenames = [
      'Maximally nutritious croque for less than one euro - Brood.csv',
      'Maximally nutritious croque for less than one euro - Kaas.csv',
      'Maximally nutritious croque for less than one euro - Hesp.csv',
    ]

    colorpairs = [
        ('cornflowerblue', 'royalblue'),
        ('mediumpurple', 'darkviolet'),
        ('salmon', 'orangered')
    ]

    for fileidx, filename in enumerate(filenames):

        # read dataframe
        df = pandas.read_csv(os.path.join(filedir, filename))
        units = df.iloc[0].to_dict()
        df.drop(0, inplace=True)
        df.reset_index()

        # parse units
        display_units = {}
        for key,val in units.items():
            if key=='name': continue
            display_val = ''
            if '(' in val: display_val = val.split('(')[1].strip(' ()')
            else: display_val = val
            display_units[key] = display_val

        # extract quantities to plot
        names = df['name'].values
        idx = np.arange(len(names))
        eff = df['eff'].values.astype(float)
        ppkg = df['ppkg'].values.astype(float)
        enpw = df['enpw'].values.astype(float)

        # make plot structure
        fig,axs = plt.subplots(figsize=(12,6), nrows=1, ncols=3)
        axs[0].barh(idx, ppkg, color=colorpairs[fileidx][0])
        axs[0].set_yticks(idx)
        axs[0].set_yticklabels(names, fontsize=12)
        axs[0].grid(axis='x')
        axs[0].set_xlabel('Price ({})'.format(display_units['ppkg']), fontsize=12)

        axs[1].barh(idx, enpw, color=colorpairs[fileidx][0])
        axs[1].set_yticks([])
        axs[1].grid(axis='x')
        axs[1].set_xlabel('Energy ({})'.format(display_units['enpw']), fontsize=12)

        axs[2].barh(idx, eff, color=colorpairs[fileidx][1])
        axs[2].set_yticks([])
        axs[2].grid(axis='x')
        axs[2].set_xlabel('Efficiency ({})'.format(display_units['eff']), fontsize=12)

        # adjust margin
        fig.subplots_adjust(left=0.3, right=0.99, wspace=0.05)

        # make title
        ingredient = os.path.splitext(filename)[0].split('-')[1].strip()
        title = 'Energy efficiency for croque ingredients: {}'.format(ingredient)
        axs[0].text(0, 1.05, title, transform=axs[0].transAxes, fontsize=15)

    plt.show()
