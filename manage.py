#!/usr/bin/env python
"""
Command-line utility for administrative tasks.

# For more information about this file, visit
# https://docs.djangoproject.com/en/2.1/ref/django-admin/
"""

import os
import sys
import pyodbc
import numpy as np
import pandas as pd


connection = pyodbc.connect('Driver={SQL Server};Server=tcp:avinash9426.database.windows.net,1433;Database=MyLotto;Uid=avinash;Pwd=Myamrita123@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
##cursor=connection.cursor()

##feedback_data = pd.read_csv('feedback.csv')
##game_order_data = pd.read_csv('game_order.csv')

cursor=connection.cursor()
cursor.execute("select * from GameOrders")
columns = [column[0] for column in cursor.description]

results = []
for row in cursor.fetchall():
    results.append(dict(zip(columns, row)))
game_order_data = pd.DataFrame(results) 

cursor=connection.cursor()
cursor.execute("select * from Feedbacks")
columns = [column[0] for column in cursor.description]

results = []
for row in cursor.fetchall():
    results.append(dict(zip(columns, row)))
feedback_data = pd.DataFrame(results) 

# cursor.close()
# connection.close()

feedback_data = feedback_data.groupby(['userid','game_id'], as_index=False).agg({
	'Rating': 'mean',
	'Feedback': lambda x: '. '.join(x)
})

user_game_ratings = feedback_data.pivot(index='userid', columns='game_id', values='Rating').fillna(3)

for game_id in user_game_ratings.columns:
	game_ratings = user_game_ratings[game_id]
	mean_rating = np.mean(game_ratings[game_ratings > 0])
	user_game_ratings[game_id][user_game_ratings[game_id] == 0] = mean_rating

game_popularity = user_game_ratings.sum().sort_values(ascending=False)

general_popular_games = game_popularity.index.tolist()
print("General Popular Games List:",general_popular_games)

query = "INSERT INTO [dbo].[Recommendation]([userid],[game_recommendation]) VALUES (" + str(1001) + ",'" + str(general_popular_games).replace('[','').replace(']','').replace(',',':').replace(' ','') + "')"
cursor.execute(query)
cursor.commit()

cursor.close()
connection.close()

if __name__ == '__main__':
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'MyFirstDjangoWeb.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
