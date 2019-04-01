

import sqlite3
import pandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
# /Users/mahindoshi/Desktop/a4.db
database_destination = input("Enter database destination : ")
q1_counter = 1
q2_counter = 1
q3_counter = 1
q4_counter = 1

def main():
    checker = '1234eE'
    while True:
        choice = input("1: Q1 \n2: Q2 \n3: Q3 \n4: Q4 \nE[e]: Exit\n")
        if(choice not in checker):
            print("Enter a valid value")
        elif choice == 'e' or choice == 'E':
            exit()
        elif choice =='1':
            question1()
        elif choice =='2':
            question2()
        elif choice == '3':
            question3()
        elif choice == '4':
            question4()


def question1():
    # shows (in a bar plot) the month-wise total count of the given
    # crime type.
    global conn, c, q1_counter

    conn = sqlite3.connect(database_destination)
    c = conn.cursor()
    while True:
        start_year = get_year("Enter start year (YYYY):")
        end_year = get_year("Enter end year (YYYY):")
        if (start_year > end_year):
            print("Try again, invalid input")
        else:
            break
    crime_type = get_crime_type("Enter crime type:")

    format_str = '''
    select Month, SUM(Incidents_Count)
    from (
    select *
    from crime_incidents
    where Crime_Type = "{crime}"

    except

    select *
    from crime_incidents
    where  Year < {start} or Year > {end})
    group by Month
    '''

    sql_command = format_str.format(crime = crime_type, start = start_year, end = end_year)

    df = pd.read_sql_query(sql_command, conn)
    plot = df.plot.bar(x = "Month")
    plt.plot()
    plt.savefig("Q1-"+ str(q1_counter) +".png")
    q1_counter +=1

def question2():
    # Given an integer N, show (in a map) the N-most populous(biggest population) and N-least populous neighborhoods with their population count.
    # population = CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE
    # we need to get:
    # Neighbourhood_Name, population, Latitude, Longitude
    global conn, c, q2_counter

    conn = sqlite3.connect(database_destination)
    c = conn.cursor()

    num_locations = get_number("Enter number of locations: ")

    # find N-most populous
    format_str1 = '''
     select p.Neighbourhood_Name, (sum(CANADIAN_CITIZEN) + sum(NON_CANADIAN_CITIZEN) + sum(NO_RESPONSE)) as number_of_people
		,Latitude, Longitude
        from population p
	inner join coordinates c on p.Neighbourhood_Name = c. Neighbourhood_Name
    group by p.Neighbourhood_Name
    having number_of_people in
    	(select (sum(CANADIAN_CITIZEN) + sum(NON_CANADIAN_CITIZEN) + sum(NO_RESPONSE)) as number_of_people
    	from population p
    	group by Neighbourhood_Name
    	order by number_of_people DESC limit {number})
    order by number_of_people DESC
    '''
    sql_command1 = format_str1.format(number = num_locations)

    # Find N-least populous
    format_str2 = '''
    select p.Neighbourhood_Name, (sum(CANADIAN_CITIZEN) + sum(NON_CANADIAN_CITIZEN) + sum(NO_RESPONSE)) as number_of_people
		,Latitude, Longitude
    from population p
    inner join coordinates c on p.Neighbourhood_Name = c.Neighbourhood_Name
    group by p.Neighbourhood_Name
    having number_of_people in
        (select (sum(CANADIAN_CITIZEN) + sum(NON_CANADIAN_CITIZEN) + sum(NO_RESPONSE)) as number_of_people
        from population p
        group by Neighbourhood_Name
        having number_of_people > 0
        order by number_of_people LIMIT {number})
    order by number_of_people
    '''
    sql_command2 = format_str2.format(number = num_locations)

    c.execute(sql_command1)
    rows1 = c.fetchall()
    c.execute(sql_command2)
    rows2 = c.fetchall()
    conn.commit()

    m = folium.Map(location=[53.5444, -113.323], zoom_start=12)
    for row in rows1:
        folium.Circle(
            location = [row[2], row[3]],  #location
            popup = str(row[0])+' ' + str(row[1]), #popup text
            radius = row[1]/10,
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

    for row in rows2:
        folium.Circle(
            location = [row[2], row[3]],  #location
            popup = str(row[0])+' ' + str(row[1]), #popup text
            radius = row[1],
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)

    m.save("Q2-"+ str(q2_counter)+ ".html")
    q2_counter +=1

def get_number(prompt):
    while True:
        try:
            num_locations = int(input(prompt))
        except ValueError:
            print("Not a valid choice")
            continue

        if num_locations < 0:
            print("Invalid number")
            continue
        else:
            break
    return num_locations

def question3():
    # initialize connection
    global conn, c
    global q3_counter

    conn = sqlite3.connect(database_destination)
    c = conn.cursor()

    # real input
    while True:
        start_year = get_year("Enter start year (YYYY):")
        end_year = get_year("Enter end year (YYYY):")
        if (start_year > end_year):
            print("Try again, invalid input")
        else:
            break

    crime_type = get_crime_type("Enter crime type:")
    number_neighborhoods = get_neighborhoods_num("Enter number of neighborhoods:")

    # main query
    format_string = '''
      select ci.Neighbourhood_Name, sum(Incidents_Count) as Counter,
              cd.Latitude, Longitude
     from crime_incidents ci
      inner join coordinates cd on ci.Neighbourhood_Name = cd.Neighbourhood_Name
      where year between '{StartYear}' and '{EndYear}'
        and Crime_Type = '{CrimeType}'
      group by ci.Neighbourhood_Name
      order by counter desc limit '{NumberNeighborhoods}';'''

    sql_command = format_string.format(StartYear = start_year,
                                       EndYear = end_year,
                                       CrimeType = crime_type,
                                       NumberNeighborhoods = number_neighborhoods)

    c.execute(sql_command)
    conn.commit()

    rows = c.fetchall()


    # create map of Edmonton
    map = folium.Map(location=(53.532223, -113.472623), zoom_start=11)

    # add circles based on query result
    for row in rows:
        folium.Circle(location = [row[2], row[3]],           # location
                      popup = row[0] + "<br> " + str(row[1]),# popup text
                      radius = row[1],                      # size of radius in meter
                      color = 'crimson',                    # color of the radius
                      fill = True,                          # whether to fill the map
                      fill_color = 'crimson'                # color to fill with
                      ).add_to(map)
    #q3counter += 1
    #print(q3counter)

    map.save("Q3-" + str(q3_counter) + ".html")

def get_year(prompt):
    while True:
        try:
            year = int(input(prompt))
            format_string = '''select Year, count(Year) as Counter from crime_incidents where Year = {Year};'''
            sql_command = format_string.format(Year = year)
            c.execute(sql_command)
            conn.commit()

            row = c.fetchone()
            if row[1] == 0:
                print("Invalid year")
                continue
            else:
                break
        except ValueError:
            print("Please enter an integer")
    return year

def get_neighborhoods_num(prompt):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Invalid entry")
            continue

        if value < 0:
            print("Invalid number")
            continue
        else:
            break
    return value

def get_crime_type(prompt):
    while True:
        value = input(prompt)

        # query against database
        c.execute("select Crime_Type, count(Crime_Type) as Counter from crime_incidents where Crime_Type = ?", [value])
        conn.commit()

        row = c.fetchone()
        #print(row[1]) is the number of crime types
        if row[1] == 0:
            print("No such crime type")
            continue
        else:
            break
    return value


def question4():
    ''' Given a range of years and an integer N, show (in a map)
    the Top-N neighborhoods with the highest crimes to population
    ratio within the provided range.
    Also, show the most frequent crime type and the ratio in each of these neighborhoods.
    '''

    global q4_counter
    # validating input
    while True:
        try:
            start_year = int(input("Enter Start Year (YYYY): "))
            end_year = int(input("Enter End Year (YYYY): "))

        except ValueError:
            print("Not a valid year, try again")
        else:
            if start_year <= end_year:
                if 2009 <= start_year <=2018:
                    break
                elif 2009 <= end_year <=2018:
                    break
                else:
                    print("out of range, try again")
            else:
                print("INVALID INPUT. TRY AGAIN")

    while True:
        try:
            num_neighbourhoods= int(input("Enter Number of Neighbourhoods: "))
        except ValueError:
            print("not a valid input")
        if num_neighbourhoods <=0:
            print("not a valid input")
        else:
            break



    q4 = sqlite3.connect(database_destination)

    # query returns the ratio of the top-n neighborhoods with the highest crimes to population
    sql_query = "select population.Neighbourhood_Name as neighbourhood, sum(crime_incidents.Incidents_Count)*1.0/sum(population.CANADIAN_CITIZEN + population.NON_CANADIAN_CITIZEN + population.NO_RESPONSE)*1.0 as ratio, coordinates.Latitude, coordinates.Longitude \
                from population, crime_incidents, coordinates \
                where crime_incidents.Neighbourhood_Name = population.Neighbourhood_Name  and coordinates.Neighbourhood_Name = population.Neighbourhood_Name and (crime_incidents.Year <={end} and crime_incidents.Year>={start}) \
                group by crime_incidents.Neighbourhood_Name \
                order by  ratio desc limit {num}".format(end = end_year, start = start_year, num = num_neighbourhoods)

    dataframe = pandas.read_sql_query(sql_query, q4)
    edmonton_map = folium.Map(location= [53.5405,-113.4990], zoom_start = 11)
    # plots the markers for top-N crime/population ratio
    for index in range(len(dataframe.index)):
        #returns the most frequent crime type in a neighbourhood
        most_popular_crime = "select crime_incidents.Crime_Type as crime_type \
                            from crime_incidents\
                            where crime_incidents.Neighbourhood_Name = \"{neighborhood_name}\" and year <= 2015 and year >= 2010\
                            group by crime_incidents.Crime_Type\
                            order by count(crime_incidents.Crime_Type) desc\
                            limit 1 ". format(neighborhood_name = dataframe["neighbourhood"][index])
        dataframe2 = pandas.read_sql_query(most_popular_crime,q4)

        popup_text = "{neighbourhood_name} \n{crime_type}\n{crime_ratio}".format(neighbourhood_name = dataframe["neighbourhood"][index],crime_type= dataframe2["crime_type"][0], crime_ratio = round(dataframe["ratio"][index],4) )
        folium.Circle([dataframe["Latitude"][index],dataframe["Longitude"][index]],
                        radius = dataframe["ratio"][index]*20000,
                        popup = popup_text,
                        color = "crimson",
                        fill = True,
                        fill_color= "crimson"
                        ).add_to(edmonton_map)
    file_name = 'Q4-{count}.html'.format(count = q4_counter)
    q4_counter = q4_counter + 1
    edmonton_map.save(file_name)

main()
