#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Visualización del Corona Virus en Venezuela
utilizando el API de https://covid19.patria.org.ve/api-covid-19-venezuela/
por David Hernandez APonte <@davidhdz> 2020
"""

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


# Dimensión de los gráficos generados
dims = (15, 8)

# Patch para leyenda del gráfico de barras de Casos nuevos
l1 = mpatches.Patch(color='#2A5CFF', alpha=0.6, label='Confirmados')
l2 = mpatches.Patch(color='#FF9028', alpha=0.6, label='Recuperados')
l3 = mpatches.Patch(color='#3ED157', alpha=0.6, label='Activos')
l4 = mpatches.Patch(color='#EB2831', alpha=0.6, label='Fallecidos')

# Personalización general de los gráficos
sns.set_style("darkgrid")
sns.set_palette("bright")

# Variables para el gráfico de distribución de casos por género
colors = ['#2A5CFF99', '#FF902899']
explode = (0.1, 0)


# Función para añadir valores encima de las barras
def show_values_on_bars(axis):
    def _show_on_single_plot(ax):
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height()
            value = '{:.0f}'.format(p.get_height())
            if int(value) > 0:
                ax.text(_x, _y, value, ha="center", size="x-small")

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)


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


    # Gráfico del número de casos registrados en Venezuela
    fig1 = plt.figure(figsize=dims)

    confirmed_lines = sns.lineplot(
        x="Date",
        y="Count",
        alpha=0.6,
        markers=True,
        marker="o",
        data=confirmados
    )
    recovered_lines = sns.lineplot(
        x="Date",
        y="Count",
        alpha=0.6,
        markers=True,
        marker="o",
        data=recuperados
    )
    actives_lines = sns.lineplot(
        x="Date",
        y="Count",
        alpha=0.6,
        markers=True,
        marker="o",
        data=activos
    )
    deaths_lines = sns.lineplot(
        x="Date",
        y="Count",
        alpha=0.6,
        markers=True,
        marker="o",
        data=fallecidos
    )

    plt.xlabel("", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Casos confirmados de COVID-19 en Venezuela",
            fontsize=15, weight='bold')
    confirmed_lines.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    confirmed_lines.figure.autofmt_xdate()
    fig1.legend(labels=['Confirmados', 'Recuperados', 'Activos',
                        'Fallecidos'], frameon=False, loc='upper center', ncol=4)

    fig1.savefig("fig1.png")


    # Gráfico del número de casos nuevos en Venezuela
    fig2 = plt.figure(figsize=dims)

    new_cases = sns.barplot(x="Date", y="vals", hue="cols",
                            data=df_nuevos, alpha=0.6, palette=["C0", "C1", "C3"], dodge=True)
    new_cases.figure.autofmt_xdate(rotation='90', ha="center")

    show_values_on_bars(new_cases)
    plt.title("Nuevos casos de COVID-19 en Venezuela", fontsize=15, weight='bold')
    plt.xlabel("", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    new_cases.legend_.remove()
    fig2.legend(handles=[l1, l2, l4], frameon=False, loc='upper center', ncol=3)

    fig2.savefig("fig2.png")


    # Gráfico de casos en Venezuela
    fig3, axes = plt.subplots(2, 2, figsize=dims, sharex=True, sharey=True)

    confirmed_bars = sns.barplot(
        x="Date", y="Count", data=confirmados, color="#2A5CFF", alpha=0.6, ax=axes[0, 0])
    recovered_bars = sns.barplot(
        x="Date", y="Count", data=recuperados, color="#FF9028", alpha=0.6, ax=axes[0, 1])
    actives_bars = sns.barplot(
        x="Date", y="Count", data=activos, color="#3ED157", alpha=0.6, ax=axes[1, 0])
    deaths_bars = sns.barplot(
        x="Date", y="Count", data=fallecidos, color="#EB2831", alpha=0.6, ax=axes[1, 1])

    show_values_on_bars(axes)
    confirmed_bars.set(xlabel='', ylabel='Cantidad de casos')
    recovered_bars.set(xlabel='', ylabel='')
    actives_bars.set(xlabel='', ylabel='Cantidad de casos')
    deaths_bars.set(xlabel='', ylabel='')
    plt.suptitle('Casos diarios de COVID-19 en Venezuela',
                fontsize=15, weight='bold')
    actives_bars.figure.autofmt_xdate(rotation='90', ha='center')
    fig3.legend(handles=[l1, l2, l3, l4], frameon=False,
                loc='lower center', ncol=4)

    fig3.savefig("fig3.png")


    # Gráfico de distribución por género de casos en Venezuela
    fig4, ax4 = plt.subplots(figsize=dims)

    ax4.pie(count_gender, labels=labels_gender, colors=colors,
            autopct=lambda p: '{:.0f}'.format(p * int(summary.Confirmed['Count']) / 100), shadow=False, startangle=90)

    centre_circle = plt.Circle((0, 0), 0.7, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.axis('equal')
    plt.title("Distribución de casos por género",
            fontsize=15, weight='bold')

    fig4.savefig("fig4.png")


    # Gráfico de distribución por edades de casos en Venezuela
    fig5, ax5 = plt.subplots(figsize=dims)

    gender_bars = sns.barplot(x="Range", y="Count", data=df_ages, alpha=0.6)

    show_values_on_bars(gender_bars)
    plt.xlabel("", fontsize=12, weight='bold')
    plt.ylabel("Cantidad de casos", fontsize=12, weight='bold')
    plt.title("Distribución de casos por edad",
            fontsize=15, weight='bold')

    fig5.savefig("fig5.png")


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

except:
    print("Ha ocurrido un error. Intente de nuevo.")