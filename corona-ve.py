#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Visualización del Corona Virus en Venezuela
utilizando el API de https://covid19.patria.org.ve/api-covid-19-venezuela/
por David Hernandez Aponte <@davidhdz> 2020-2021
"""

# import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num
import numpy as np
import pandas as pd
import matplotlib.cm as cm
import sys


# Dimensión de los gráficos generados
dims = (20, 11)

# Personalización general de los gráficos
plt.style.use('seaborn-darkgrid')
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.titleweight'] = 'bold'


# Función para añadir valores encima de las gráficas
def show_values_on_bars(axs,maxv):
    def _show_on_single_plot(ax):
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height() + maxv*.01
            value = '{:.0f}'.format(p.get_height())
            if int(value) > 0:
                ax.text(_x, _y, value, ha="center", size="small")
    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)

def show_values_on_lines(x,y):
        #for i,j in zip(x,y):
            #if int(j) > 0:
                #ax.annotate(str(j),xy=(i,j), xytext=(-5,6), textcoords='offset points', size="x-small")
        ax.annotate(str(y),xy=(x,y), xytext=(5,-1), textcoords='offset points', size="x-small")


# Carga de datos y generación de Data frames para los gráficos de línea de tiempo
try:
    timeline = pd.read_json('https://covid19.patria.org.ve/api/v1/timeline')
    timeline['Date'] = timeline['Date'].dt.date
    df_confirmed = pd.DataFrame(timeline.Confirmed.values.tolist())
    df_recovered = pd.DataFrame(timeline.Recovered.values.tolist())
    df_deaths = pd.DataFrame(timeline.Deaths.values.tolist())
    df_actives = df_confirmed - df_recovered - df_deaths

    confirmados = pd.concat([timeline['Date'], df_confirmed], axis=1)
    recuperados = pd.concat([timeline['Date'], df_recovered], axis=1)
    fallecidos = pd.concat([timeline['Date'], df_deaths], axis=1)
    activos = pd.concat([timeline['Date'], df_actives], axis=1)
    nuevos = pd.concat([timeline['Date'], df_confirmed['New'],
                        df_recovered['New'], df_deaths['New']], axis=1)
    nuevos.columns = ['Date', 'New_Confirmed', 'New_Recovered', 'New_Death']
    df_nuevos = nuevos.melt('Date', var_name='cols',  value_name='vals')
    last_report = timeline.iloc[-1]


    # Carga de datos y generación de Data frames para los gráficos de resúmen
    summary = pd.read_json('https://covid19.patria.org.ve/api/v1/summary')

    hombres = summary.Confirmed['ByGender']['male']
    mujeres = summary.Confirmed['ByGender']['female']
    labels_gender = ['Hombres', 'Mujeres']
    count_gender = [hombres, mujeres]
    data = {'Gender': labels_gender,
            'Count': count_gender}
    df_gender = pd.DataFrame(data)
    df_ages = pd.DataFrame(
        summary.Confirmed['ByAgeRange'].items(), columns=["Range", "Count"])
    df_states = pd.DataFrame(
        summary.Confirmed['ByState'].items(), columns=["State", "Count"])


    # Gráfico del número de casos registrados en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    ax.plot(confirmados["Date"], confirmados["Count"],
            '-', label='Confirmados (acumulados)', alpha=0.8)
    show_values_on_lines(confirmados["Date"].iloc[-1], confirmados["Count"].iloc[-1])
    ax.plot(recuperados["Date"], recuperados["Count"],
            '-', label='Recuperados (acumulados)', alpha=0.8)
    show_values_on_lines(recuperados["Date"].iloc[-1], recuperados["Count"].iloc[-1])
    ax.plot(activos["Date"], activos["Count"],
            '-', label='Activos (acumulados)', alpha=0.8)
    show_values_on_lines(activos["Date"].iloc[-1], activos["Count"].iloc[-1])
    ax.plot(fallecidos["Date"], fallecidos["Count"],
            '-', label='Fallecidos (acumulados)', alpha=0.8)
    show_values_on_lines(fallecidos["Date"].iloc[-1], fallecidos["Count"].iloc[-1])
    #ax.bar(nuevos["Date"],nuevos["New_Confirmed"],color='C6')
    ax.plot(nuevos["Date"], nuevos["New_Confirmed"],
            '-', label='Confirmados (diarios)', color='black', alpha=0.8)
    show_values_on_lines(nuevos["Date"].iloc[-1], nuevos["New_Confirmed"].iloc[-1])
    plt.xticks(rotation=45, ha='center')
    plt.xlabel("")
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos de COVID-19 en Venezuela al "+last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 5))
    myFmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.legend(loc='upper left', fontsize=12)
    plt.savefig("fig1.png")



    # Gráfico del número de casos nuevos en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    x = date2num(nuevos['Date'])
    barwidth = .3
    bar1 = ax.bar(x - barwidth, nuevos["New_Confirmed"],
                width=barwidth, label='Confirmados', alpha=0.8)
    bar2 = ax.bar(x, nuevos["New_Recovered"],
                width=barwidth, label='Recuperados', alpha=0.8)
    bar3 = ax.bar(x + barwidth, nuevos["New_Death"],
                width=barwidth, label='Fallecidos', color='C3', alpha=0.8)
    plt.xticks(rotation=45, ha='center')
    start, end = ax.get_xlim()
    #ax.xaxis.set_ticks(np.arange(start, end, 5))
    #show_values_on_bars(ax)
    plt.xlabel("")
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos diarios de COVID-19 en Venezuela al "+last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    myFmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.legend(loc='upper left', fontsize=12)
    plt.savefig("fig2.png")


    #    # Gráfico de casos en Venezuela
    #    fig, ((ax1, ax2, ax3, ax4)) = plt.subplots(
    #        4, figsize=dims, sharex=True, sharey=True)
    #    fig.tight_layout(pad=4.0)
    #    ax1.bar(confirmados["Date"], confirmados["Count"], color='C0', alpha=0.8)
    #    ax1.set_title('Confirmados')
    #    #show_values_on_bars(ax1)
    #    ax2.bar(recuperados["Date"], recuperados["Count"], color='C1', alpha=0.8)
    #    ax2.set_title('Recuperados')
    #    #show_values_on_bars(ax2)
    #    ax3.bar(activos["Date"], activos["Count"], color='C2', alpha=0.8)
    #    ax3.set_title('Activos')
    #    #show_values_on_bars(ax3)
    #    ax4.bar(fallecidos["Date"], fallecidos["Count"], color='C3', alpha=0.8)
    #    ax4.set_title('Fallecidos')
    #    #show_values_on_bars(ax4)
    #    plt.xticks(rotation=45, ha='right')
    #    plt.suptitle('Casos de COVID-19 en Venezuela (acumulados)',
    #                fontsize=15, weight='bold')
    #    for ax in fig.get_axes():
    #        ax.set(
    #            xlabel='',
    #            ylabel='Cantidad de casos',
    #            xticks=(nuevos['Date']),
    #        )
    #        ax.label_outer()
    #    plt.savefig("fig3.png")


    # Gráfico de distribución por género de casos en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    ax.pie(count_gender, labels=labels_gender, colors=['C0', 'C1'], wedgeprops={'alpha':0.8},
        autopct=lambda p: '{:.0f}'.format(p * int(summary.Confirmed['Count']) / 100), shadow=False, startangle=90)
    # centre_circle = plt.Circle((0, 0), 0.7, fc='white')
    fig = plt.gcf()
    # fig.gca().add_artist(centre_circle)
    plt.axis('equal')
    plt.title("Distribución de casos por género al "+last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    fig.savefig("fig4.png")


    # Gráfico de distribución por edades de casos en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    ax.bar(df_ages["Range"], df_ages["Count"], color=['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'], alpha=0.8)
    maxv=max(df_ages["Count"])
    show_values_on_bars(ax,maxv)
    plt.xlabel("Rango de edad", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Distribución de casos por edad al "+last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    fig.savefig("fig5.png")


    # Gráfico de distribución por estados
    fig, ax = plt.subplots(figsize=dims)
    colors = cm.rainbow(np.linspace(1, 0, len(df_states["State"])))
    df_states.sort_values(by=['Count'], inplace=True, ascending=False)
    ax.bar(df_states["State"], df_states["Count"], color=colors, alpha=0.8)
    maxv=max(df_states["Count"])
    show_values_on_bars(ax,maxv)
    plt.xlabel("Entidad", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Distribución de casos por estado al "+last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    plt.xticks(rotation=45, )
    fig.savefig("fig6.png")


    # Salida por cónsola
    print()
    print("Casos COVID-19 en Venezuela")
    print("===========================")
    print("Confirmados: \t",  int(summary.Confirmed['Count']))
    print("Recuperados: \t",  int(summary.Recovered['Count']))
    print("Fallecidos: \t",  int(summary.Deaths['Count']))
    print("Activos: \t",  int(summary.Active['Count']))
    print()
    print("Nuevos casos al", last_report['Date'].strftime('%d/%m/%Y'))
    print("===========================")
    print("Confirmados: \t",  int(last_report['Confirmed']['New']))
    print("Recuperados: \t",  int(last_report['Recovered']['New']))
    print("Fallecidos: \t",  int(last_report['Deaths']['New']))
    print()
    print("Estadísticas")
    print("===========================")
    print("Letalidad: \t{0:3.2f}%".format(
        (int(summary.Deaths['Count'])/int(summary.Confirmed['Count']))*100))
    print("Recuperación: \t{0:3.2f}%".format(
        (int(summary.Recovered['Count'])/int(summary.Confirmed['Count']))*100))
    print()

except:
    print("Ha ocurrido un error:", sys.exc_info()[0])
