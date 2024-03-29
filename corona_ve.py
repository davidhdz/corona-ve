#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Visualización del Corona Virus en Venezuela
utilizando el API de https://covid19.patria.org.ve/api-covid-19-venezuela/
por David Hernandez Aponte <@davidhdz> 2020-2021
"""

import sys
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.dates import date2num

# Dimensión de los gráficos generados
dims = (20, 11)

# Personalización general de los gráficos
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.titleweight'] = 'bold'


# Función para añadir valores encima de las gráficas
def show_values_on_bars(axs, max_v):
    """Prints values above the bars"""
    def _show_on_single_plot(axx):
        for patch in axx.patches:
            ancho = patch.get_width()
            alto = patch.get_height()
            _x = patch.get_x() + ancho / 2
            _y = patch.get_y() + alto + max_v*.01
            value = f'{alto:.0f}'
            if int(value) > 0:
                axx.text(_x, _y, value, ha="center", size="small")
    if isinstance(axs, np.ndarray):
        for _, ax_val in np.ndenumerate(axs):
            _show_on_single_plot(ax_val)
    else:
        _show_on_single_plot(axs)


def show_values_on_lines(x_value, y_value):
    """Prints values at the end of lines"""
    # for i,j in zip(x,y):
    # if int(j) > 0:
    #ax.annotate(str(j),xy=(i,j), xytext=(-5,6), textcoords='offset points', size="x-small")
    ax.annotate(str(y_value), xy=(x_value, y_value), xytext=(5, -1),
                textcoords='offset points', size="x-small")


# Carga de datos y generación de Data frames para los gráficos de línea de tiempo
try:
    ARGS = len(sys.argv)-1
    timeline = pd.read_json('https://covid19.patria.org.ve/api/v1/timeline')
    timeline['Date'] = timeline['Date'].dt.date
    f_ini = timeline['Date'].iloc[0]
    f_fin = timeline['Date'].iloc[-1]
    f_fin2 = timeline.iloc[-1]

    if ARGS > 0:
        try:
            f_ini = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            if ARGS == 2:
                f_fin = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()

            mask = (timeline['Date'] >= f_ini) & (timeline['Date'] <= f_fin)
            timeline = timeline.loc[mask].reset_index()
        except ValueError:
            print(
                "Error en formato de fecha, use el siguiente formato: YYYY-MM-DD o YYYY-M-D")
            print("Se usarán los rangos de fecha predeterminados.")

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
    first_report = timeline.iloc[0]
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
    show_values_on_lines(
        confirmados["Date"].iloc[-1], confirmados["Count"].iloc[-1])
    ax.plot(recuperados["Date"], recuperados["Count"],
            '-', label='Recuperados (acumulados)', alpha=0.8)
    show_values_on_lines(
        recuperados["Date"].iloc[-1], recuperados["Count"].iloc[-1])
    ax.plot(activos["Date"], activos["Count"],
            '-', label='Activos (acumulados)', alpha=0.8)
    show_values_on_lines(activos["Date"].iloc[-1], activos["Count"].iloc[-1])
    ax.plot(fallecidos["Date"], fallecidos["Count"],
            '-', label='Fallecidos (acumulados)', alpha=0.8)
    show_values_on_lines(
        fallecidos["Date"].iloc[-1], fallecidos["Count"].iloc[-1])
    # ax.bar(nuevos["Date"],nuevos["New_Confirmed"],color='C6')
    ax.plot(nuevos["Date"], nuevos["New_Confirmed"],
            '-', label='Confirmados (diarios)', color='black', alpha=0.8)
    show_values_on_lines(nuevos["Date"].iloc[-1],
                         nuevos["New_Confirmed"].iloc[-1])
    plt.xticks(rotation=45, ha='center')
    plt.xlabel("")
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos de COVID-19 en Venezuela del " +
              first_report['Date'].strftime('%d/%m/%Y') + " al " +
              last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 5))
    myFmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.legend(loc='upper left', fontsize=12)
    plt.savefig("fig1.png")

    # Gráfico del número de casos confirmados en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    ax.plot(nuevos['Date'], nuevos["New_Confirmed"],
            '-', label='Confirmados (acumulados)', alpha=0.8)
    # ax.bar(nuevos['Date'], nuevos["New_Confirmed"],
    #   width=1, label='Confirmados', alpha=0.8)
    # show_values_on_lines(
    # nuevos['Date'].iloc[-1], nuevos["New_Confirmed"].iloc[-1])
    # ax.bar(nuevos["Date"],nuevos["New_Confirmed"],color='C6')
    plt.xticks(rotation=45, ha='center')
    plt.xlabel("")
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos Diarios Confirmados de COVID-19 en Venezuela del " +
              first_report['Date'].strftime('%d/%m/%Y') + " al " +
              last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 5))
    myFmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.legend(loc='upper left', fontsize=12)
    plt.savefig("fig2.png")

    # Gráfico del número de casos nuevos en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    x = date2num(nuevos['Date'])
    BARWIDTH = .3
    bar1 = ax.bar(x - BARWIDTH, nuevos["New_Confirmed"],
                  width=BARWIDTH, label='Confirmados', alpha=0.8)
    bar2 = ax.bar(x, nuevos["New_Recovered"],
                  width=BARWIDTH, label='Recuperados', alpha=0.8)
    bar3 = ax.bar(x + BARWIDTH, nuevos["New_Death"],
                  width=BARWIDTH, label='Fallecidos', color='C3', alpha=0.8)
    plt.xticks(rotation=45, ha='center')
    # show_values_on_bars(ax)
    plt.xlabel("")
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos diarios de COVID-19 en Venezuela del " +
              first_report['Date'].strftime('%d/%m/%Y') + " al " +
              last_report['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    # start, end = ax.get_xlim()
    #ax.xaxis.set_ticks(np.arange(start, end, 5))
    myFmt = mdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(myFmt)
    ax.legend(loc='upper left', fontsize=12)
    plt.savefig("fig3.png")

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
    ax.pie(count_gender, labels=labels_gender, colors=['C0', 'C1'], wedgeprops={'alpha': 0.8},
           autopct=lambda p: f"{p * int(summary.Confirmed['Count']) / 100:.0f}",
           shadow=False, startangle=90)
    # centre_circle = plt.Circle((0, 0), 0.7, fc='white')
    fig = plt.gcf()
    # fig.gca().add_artist(centre_circle)
    plt.axis('equal')
    plt.title("Distribución de casos por género al " +
              f_fin2['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    fig.savefig("fig4.png")

    # Gráfico de distribución por edades de casos en Venezuela
    fig, ax = plt.subplots(figsize=dims)
    ax.bar(df_ages["Range"], df_ages["Count"], color=[
        'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'], alpha=0.8)
    maxv = max(df_ages["Count"])
    show_values_on_bars(ax, maxv)
    plt.xlabel("Rango de edad", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Distribución de casos por edad al " +
              f_fin2['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    fig.savefig("fig5.png")

    # Gráfico de distribución por estados
    fig, ax = plt.subplots(figsize=dims)
    colors = cm.rainbow(np.linspace(1, 0, len(df_states["State"])))
    df_states.sort_values(by=['Count'], inplace=True, ascending=False)
    ax.bar(df_states["State"], df_states["Count"], color=colors, alpha=0.8)
    maxv = max(df_states["Count"])
    show_values_on_bars(ax, maxv)
    plt.xlabel("Entidad", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Distribución de casos por estado al " +
              f_fin2['Date'].strftime('%d/%m/%Y'), fontsize=18, weight='bold')
    plt.xticks(rotation=45, )
    fig.savefig("fig6.png")

    # Salida por cónsola
    letalidad = int(summary.Deaths['Count'])/int(summary.Confirmed['Count'])*100
    recuperacion = int(summary.Recovered['Count'])/int(summary.Confirmed['Count'])*100
    print()
    print("Casos COVID-19 en Venezuela")
    print("===========================")
    print("Confirmados: \t",  int(summary.Confirmed['Count']))
    print("Recuperados: \t",  int(summary.Recovered['Count']))
    print("Fallecidos: \t",  int(summary.Deaths['Count']))
    print("Activos: \t",  int(summary.Active['Count']))
    print()
    print("Estadísticas")
    print("===========================")
    print(f"Letalidad: \t{letalidad:3.2f}%")
    print(f"Recuperación: \t{recuperacion:3.2f}%")
    print()
    print("Casos del día ", last_report['Date'].strftime('%d/%m/%Y'))
    print("===========================")
    print("Confirmados: \t",  int(last_report['Confirmed']['New']))
    print("Recuperados: \t",  int(last_report['Recovered']['New']))
    print("Fallecidos: \t",  int(last_report['Deaths']['New']))
    print()
except SystemError as err:
    print("Ha ocurrido un error:", err)
    print()
