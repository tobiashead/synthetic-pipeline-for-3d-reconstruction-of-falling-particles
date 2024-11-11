import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from pathlib import Path


def add_arrow_if_value_out_of_range(ax, PSets,column,y_limit,colors,arrows_color,direction):
        if direction == "above":
            limit_condition =PSets[column] > y_limit[1]
        if direction == "below":
            limit_condition =PSets[column] < y_limit[0]
        limit_index = np.where(limit_condition)[0]
        limit = PSets[limit_condition]
        for j, x_pos in enumerate(limit.index):
            color = arrows_color if arrows_color is not None else colors.iloc[limit_index[j]]
            if direction == "above":
                ax.annotate(
                    '', 
                    xy=(x_pos, y_limit[1]), xycoords='data',  # Endpunkt des Pfeils auf y-Grenze
                    xytext=(x_pos, y_limit[1] - (0.05 * (y_limit[1] - y_limit[0]))), textcoords='data',  # Startpunkt des Pfeils knapp darunter
                    arrowprops=dict(edgecolor=color,facecolor='black', arrowstyle='->')
                )
            if direction == "below":
                ax.annotate(
                    '', 
                    xy=(x_pos, y_limit[0]), xycoords='data',  # Endpunkt des Pfeils auf unterem y-Grenze
                    xytext=(x_pos, y_limit[0] + (0.05 * (y_limit[1] - y_limit[0]))), textcoords='data',  # Startpunkt des Pfeils knapp darüber
                    arrowprops=dict(edgecolor=color,facecolor="red", arrowstyle='->')
                )

            
def plot_4_quality_criteria(PSets_Eval_small_qual, savefig_folder, figsize, xlabel, marker,markersize, 
                            arrows_color, font_size, labelpad, xticks, grid,
                            one_decimal_place, plot_x0_line, markersize_legend, legend_loc, optimal_span, y_limits,
                            mark_base_case = None, yticks = None):

    # Define Data Set
    PSets = PSets_Eval_small_qual
    
    # Lade Thesis Plot Style
    parent_dir = Path(__file__).resolve().parent.parent
    style_path = parent_dir / 'thesis.mplstyle'
    plt.style.use(str(style_path))
    
    # Farbzuordnung basierend auf quality index
    color_map = {0: 'red', 1: 'orange', 2: 'green'}
    colors = PSets["quality_index"].map(color_map)


    # Titel für die einzelnen Subplots
    #title = ["Positionsfehler", "Positionsfehlerquote", "Volumenfehler", "Sphärizitätsfehler"]
    labels = ["$r_{PF}$ in %", "$r_{PFQ}$ in %", "$r_{v}$ in %", "$r_\Psi$ in %"]

    # Erstelle 2x2 Subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=figsize)  # Größere Größe für 2x2 Layout

    # Spaltennamen aus dem DataFrame
    columns = PSets.columns
    columns = columns[0:4]
    
    # Iteriere über die Spalten und Plots
    for i, column in enumerate(columns):
        ax = axes[i // 2, i % 2]  # Umrechnung für 2x2-Layout
        ax.scatter(PSets.index, PSets[column], color=colors,marker=marker,s=markersize,zorder= 10)
        
        # Setze die y-Limits für den jeweiligen Subplot
        y_limit = y_limits[i]
        ax.set_ylim(y_limit)
        
        # Prüfe auf Werte über dem oberen y-Limit und füge Pfeile hinzu
        add_arrow_if_value_out_of_range(ax, PSets,column,y_limit,colors,arrows_color,direction="above")
        # Prüfe auf Werte untem dem unteren y-Limit und füge Pfeile hinzu
        add_arrow_if_value_out_of_range(ax, PSets,column,y_limit,colors,arrows_color,direction="below")
        
        # Anpassungen der Achsenbeschriftungen
        if i >= len(columns) - 2:
            ax.set_xlabel(xlabel, fontsize=font_size)
        ax.set_ylabel(labels[i], fontsize=font_size, labelpad=labelpad[i])

    # Passe die Schriftgröße der Ticks an
    for ax in axes.flatten():
        ax.tick_params(axis='both', which='major', labelsize=font_size)

    # Passe den Platz zwischen den Subplots an
    plt.subplots_adjust(hspace=0.2, wspace=0.3)


    if xticks is not None:
        for ax in axes.flat: 
            ax.set_xlim([xticks[0], xticks[-1]])
            ax.set_xticks(xticks)
    if yticks is not None:        
        for i,ax in enumerate(axes.flat):
            if yticks[i] is not None: 
                #ax.set_ylim([yticks[i][0], yticks[i][-1]])
                ax.set_yticks(yticks[i])    
    if one_decimal_place:        
        for ax in axes.flat:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.1f}'))       
    if grid: 
        for ax in axes.flat: 
            ax.grid(True,zorder=0)
            
    if plot_x0_line:
        for ax in axes.flat: 
            ax.axhline(y=0, color='black', linestyle='--',linewidth=1)

    # Define legend elements based on color_map
    legend_elements = [Line2D([0], [0], marker=marker, color='w', label='$I_q=$ {}'.format(quality_index),
                            markerfacecolor=color, markersize=markersize_legend, markeredgewidth=0)
                    for quality_index, color in color_map.items()]

    # Add the legend to the specific subplot
    axes[0,1].legend(handles=legend_elements, loc=legend_loc,fontsize=font_size,
                    borderpad=0.2,handlelength=1,handletextpad=0.3,labelspacing=0.1)

    # Graues, transparentes Intervall auf der x-Achse
    if optimal_span is not None:
        for ax in axes.flat: 
            ax.axvspan(optimal_span[0], optimal_span[1], color='gray', alpha=0.2, linestyle  = "-",linewidth = 0)  # alpha steuert die Transparenz (0=voll transparent, 1=voll deckend)
            ax.axvline(optimal_span[0], color='grey', linewidth=0.5,  linestyle = "-")  # Linke Linie
            ax.axvline(optimal_span[1], color='grey', linewidth=0.5, linestyle = "-")  # Rechte Linie
    if mark_base_case is not None:
        for ax in axes.flat: 
            ax.axvline(x=mark_base_case, color='black', linestyle='-.',linewidth=0.6)


    # Plot anzeigen und speichern
    if savefig_folder is not None:
        plt.savefig(Path(savefig_folder) / "criterions_4figures.pdf", format="pdf",bbox_inches="tight")
        plt.savefig(Path(savefig_folder)  / "criterions_4figures.svg", format="svg",bbox_inches="tight")
    plt.show()
    
    return fig, axes