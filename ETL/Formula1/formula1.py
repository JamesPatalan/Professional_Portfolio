import pandas as pd
import re
import json
import requests
from datetime import datetime
import ast
import sqlite3
import numpy as np
import matplotlib.pyplot as plt

# Weird placements
fours = ['https://en.wikipedia.org/wiki/2018_Azerbaijan_Grand_Prix',
    'https://en.wikipedia.org/wiki/2018_Monaco_Grand_Prix',
    'https://en.wikipedia.org/wiki/2018_British_Grand_Prix',
    'https://en.wikipedia.org/wiki/2018_Belgian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2018_Russian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2019_Russian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2019_Spanish_Grand_Prix',
    'https://en.wikipedia.org/wiki/2019_French_Grand_Prix', 
    'https://en.wikipedia.org/wiki/2020_Hungarian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2020_Russian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2020_Sakhir_Grand_Prix',
    'https://en.wikipedia.org/wiki/2021_Italian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2021_Sao_Paulo_Grand_Prix',
    'https://en.wikipedia.org/wiki/2022_Emilia_Romagna_Grand_Prix',
    'https://en.wikipedia.org/wiki/2022_Austrian_Grand_Prix',
    'https://en.wikipedia.org/wiki/2022_Sao_Paulo_Grand_Prix',
    'https://en.wikipedia.org/wiki/2022_Singapore_Grand_Prix',
    'https://en.wikipedia.org/wiki/2022_Japanese_Grand_Prix']

ones = ['https://en.wikipedia.org/wiki/2021_British_Grand_Prix',
    'https://en.wikipedia.org/wiki/2018_Abu_Dhabi_Grand_Prix',
    'https://en.wikipedia.org/wiki/2019_French_Grand_Prix',
    'https://en.wikipedia.org/wiki/2019_Spanish_Grand_Prix']


def create_season_url_lst():
    season_url_lst = []

    for year in range(2018,2023):    

        season_url = f'https://en.wikipedia.org/wiki/{year}_Formula_One_World_Championship'
        season_url_lst.append(season_url)
        
    return season_url_lst


def create_races_by_season_lst(season_url_lst):
    races_by_season_lst = []

    # Find the table that contains all of the races in the given season
    for url in season_url_lst:
        data = pd.read_html(url)
        data = data[2]

        if '2020' in url:
            data = data[~data["Grand Prix"].str.contains('70th Anniversary Grand Prix')]

        # Clean the table to remove whitespaces and put race names into a list
        data.replace(' ', '_', regex=True, inplace=True)

        grand_prix_lst = []

        for i in data['Grand Prix']:
            grand_prix_lst.append(i)

        # Remove the 'source' value that was scraped from the table by accident
        grand_prix_lst.pop()

        races_by_season_lst.append(grand_prix_lst)
        
    return races_by_season_lst
        
def create_master_url_lst(races_by_season_lst):
    master_url_lst = []
    year = 2018

    # Loop through the list of seasons and create proper urls
    for season in races_by_season_lst:
        for race in season:

            # Fixes error caused by special character
            if 'ã' in race:
                race = race.replace('ã', 'a')

            race_name = f'{year}_{race}'
            race_url = f"https://en.wikipedia.org/wiki/{year}_{race}"
            master_url_lst.append((race_url, race_name))

        # Increase the counter variable once the season has been completed
        year += 1
        
    return master_url_lst


# Create races dict
def get_race_data(master_url_lst):
    dataframes_lst = []
    dataframes_dict = {}

    # Iterates through the list of tuples and adds each df to the dictionary and list, saved under its name
    for url, race in master_url_lst:
        max_rows = 20

        # Checks for URLS with odd table placements
        if url in fours:
            data = pd.read_html(url)
            data = data[4]

         elif url in ones:
            data = pd.read_html(url)
            data = data[1]

        elif 'https://en.wikipedia.org/wiki/2018_Abu_Dhabi_Grand_Prix' in url:
            data = pd.read_html(url)
            data = data[5]
        
        elif 'https://en.wikipedia.org/wiki/2021_British_Grand_Prix' in url:
            data = pd.read_html(url)
            data = data[5]

        elif 'https://en.wikipedia.org/wiki/2019_Hungarian_Grand_Prix' in url:
            data = pd.read_html(url)
            data = data[7]

        else:
            data = pd.read_html(url)
            data = data[3]

        # Removes fastest lap row and source row
        if len(data) > max_rows:
            data = data.iloc[:max_rows]
            
        # Add race name column
        data['Race_Name'] = race

        dataframes_dict[race] = data
        dataframes_lst.append(data)
            
    return dataframes_lst, dataframes_dict


def clean_df(driver_df):
    # Drop unneeded columns
    driver_df = driver_df.drop(['Laps1', 'Start', 'Points1', 'Unnamed: 8', 'Laps2'], axis=1)

    # Fix dtypes, Pos (end position) and Grid (start position) must be numeric
    driver_df['Pos.'] = pd.to_numeric(driver_df['Pos.'], errors='coerce')
    driver_df['Grid'] = pd.to_numeric(driver_df['Grid'], errors='coerce')

    # Count Retires or PL starts as 20
    driver_df = driver_df.fillna(20)

    return driver_df


def sql_table(driver_df):
    conn = sqlite3.connect('formula1.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS drivers (End_Pos REAL, No TEXT, Driver TEXT, Constructor TEXT,
    Laps TEXT, TimeRetired TEXT, Start_Pos REAL, Points TEXT, Race_Name TEXT)''')

    for row in driver_df.itertuples():
    c.execute(
        'INSERT INTO drivers (End_Pos, No, Driver, Constructor, Laps, TimeRetired, Start_Pos, Points, Race_Name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
    )

    formula1 = pd.read_sql('SELECT * FROM drivers', conn)

    conn.close()

    return formula1


def clean_table(formula1):
    formula1['Start_Pos'] = pd.to_numeric(formula1['Start_Pos'], errors='coerce')
    formula1['End_Pos'] = pd.to_numeric(formula1['End_Pos'], errors='coerce')

    formula1 = formula1.fillna(20)

    formula1['Gain-Loss'] = formula1['Start_Pos'] - formula1['End_Pos']


def standardize_names(team_name):
    if 'Alfa' in team_name or 'Sauber' in team_name:
        return 'Alfa Romeo'
    elif 'AlphaTauri' in team_name or 'Toro Rosso' in team_name:
        return 'AlphaTauri'
    elif 'McLaren' in team_name:
        return 'McLaren'
    elif 'Red Bull' in team_name:
        return 'Red Bull'
    elif 'Renault' in team_name:
        return 'Alpine'
    elif 'Aston' in team_name or 'Force' in team_name or 'Racing' in team_name:
        return 'Aston Martin'
    else:
        return team_name



def constructor(formula1):
    ax = plt.axes()
    formula1.groupby('Constructor')['Gain-Loss'].mean().plot(kind='bar', color='blue')
    plt.suptitle('Average Gain-Loss by Constructor', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    plt.xlabel('Constructor', weight='bold')
    plt.xticks(rotation=45)
    plt.ylabel('Average Gain-Loss', weight='bold')
    ax.set_facecolor('silver')
    plt.show()


def verstappen(formula1):
    verstappen_df = formula1[formula1['Driver'] == 'Max Verstappen']
    
    ax = plt.axes()
    plt.hist(verstappen_df['End_Pos'], color='black', edgecolor='ivory', bins=20)
    plt.xlabel('Position', weight='bold')
    plt.ylabel('Frequency', weight='bold')
    plt.suptitle('Finishing Positions of Max Verstappen', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    ax.set_facecolor('silver')
    plt.xticks(np.arange(1, 21, 1))
    plt.show()


def hamilton(formula1):
    hamilton_df = formula1[formula1['Driver'] == 'Lewis Hamilton']

    ax = plt.axes()
    plt.hist(hamilton_df['End_Pos'], color='teal', edgecolor='black', bins=20)
    plt.xlabel('Position', weight='bold')
    plt.ylabel('Frequency', weight='bold')
    plt.suptitle('Finishing Positions of Lewis Hamilton', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    ax.set_facecolor('silver')
    plt.xticks(np.arange(1, 21, 1))
    plt.show()


def russel(formula1):
    russel_df = formula1[formula1['Driver'] == 'George Russell']

    ax = plt.axes()
    plt.hist(russel_df['End_Pos'], color='teal', edgecolor='black', bins=20)
    plt.xlabel('Position', weight='bold')
    plt.ylabel('Frequency', weight='bold')
    plt.suptitle('Finishing Positions of George Russell', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    ax.set_facecolor('silver')
    plt.xticks(np.arange(1, 21, 1))
    plt.show()


def norris(formula1):
    norris_df = formula1[formula1['Driver'] == 'Lando Norris']

    ax = plt.axes()
    plt.hist(norris_df['End_Pos'], color='orange', edgecolor='black', bins=20)
    plt.xlabel('Position', weight='bold')
    plt.ylabel('Frequency', weight='bold')
    plt.suptitle('Finishing Positions of Lando Norris', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    ax.set_facecolor('silver')
    plt.tight_layout()
    plt.xticks(np.arange(1, 21, 1))
    plt.show()


def leclerc(formula1):
    leclerc_df = formula1[formula1['Driver'] == 'Charles Leclerc']

    ax = plt.axes()
    plt.hist(leclerc_df['End_Pos'], color='red', edgecolor='black', bins=20)
    plt.xlabel('Position', weight='bold')
    plt.ylabel('Frequency', weight='bold')
    plt.suptitle('Finishing Positions of Charles Leclerc', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    ax.set_facecolor('silver')
    plt.xticks(np.arange(1, 21, 1))
    plt.show()


def standardize_drivers(driver):
    if 'Nikita' in driver:
        return 'Nikita Mazepin'
    else:
        return driver
    

def gl_drivers(formula1):
    ax = plt.axes()
    formula1.groupby('Driver')['Gain-Loss'].mean().plot(kind='bar', color=('black', 'black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','black','red','black','black','black','green'))
    plt.suptitle('Average Gain-Loss by Driver', weight='bold')
    plt.title('Data Scraped from Wikipedia')
    plt.xlabel('Driver', weight='bold')
    plt.ylabel('Average Gain-Loss', weight='bold')
    ax.set_facecolor('silver')
    plt.show()


def main():
    
    season_url_lst = create_season_url_lst()
    races_by_season_lst = create_races_by_season_lst(season_url_lst)
    master_url_lst = create_master_url_lst(races_by_season_lst)
    dataframes_lst, dataframes_dict = get_race_data(master_url_lst)
    
    # Consolodate DFs
    driver_df = pd.concat(dataframes_lst)

    # Create table
    driver_df = clean_df(driver_df)
    formula1 = sql_table(driver_df)
    formula1 = clean_table(formula1)
    formula1['Constructor'] = formula1['Constructor'].apply(standardize_names)

    # Visualizations
    constructor(formula1)
    verstappen(formula1)
    hamilton(formula1)
    russel(formula1)
    norris(formula1)
    leclerc(formula1)

    formula1['Driver'] = formula1['Driver'].apply(standardize_drivers)
    gl_drivers(formula1)


if __name__ == '__main__':
    main()
