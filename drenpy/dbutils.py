import os
import logging
import psycopg2
import atexit
import pangres
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

load_dotenv()


def db_disconnect(db_connection=None):
    logging.info("Disconnecting from database")
    db_connection.close()


def db_connector(n_tries=4):
    for db_try in range(n_tries):
        try:
            print('CONNECTION ATTEMPt')
            conn = psycopg2.connect(dbname=os.getenv("POSTGRES_DB"),
                                    user=os.getenv("POSTGRES_USER"),
                                    host=os.getenv("POSTGRES_HOST"),
                                    password=os.getenv("POSTGRES_PASSWORD"),
                                    port=os.getenv("POSTGRES_PORT"))
            atexit.register(db_disconnect, db_connection=conn)
            logging.info("Connected to DB")
            return conn
        except psycopg2.OperationalError:
            if db_try + 1 == n_tries:
                logging.error('Unable to connect to the database')
                raise
            else:
                logging.error(f"Failure to connect to the DB, on try {db_try + 2}")


def alchemy_connector(user=None, password=None, host=None, db=None):
    if user is None:
        user = os.getenv("POSTGRES_USER")
    if password is None:
        password = os.getenv("POSTGRES_PASSWORD")
    if host is None:
        host = os.getenv("POSTGRES_HOST")
    if db is None:
        db = os.getenv("POSTGRES_DB")

    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{db}')
    return engine


def load_tables():
    # Get connection to database
    engine = alchemy_connector()
    if not engine.has_table('flights'):
        logging.info('Building Flights')
        df = pd.read_csv(
            "https://raw.githubusercontent.com/vaibhavwalvekar/NYC-Flights-2013-Dataset-Analysis/master/flights.csv")
        df['index'] = np.arange(len(df))
        df.set_index('index', inplace=True)
        pangres.upsert(engine=engine, df=df, schema='public', table_name='flights', if_row_exists='update')
    else:
        logging.info('Skipping flights table creation')

    if not engine.has_table('wine'):
        logging.info('Building Wine')
        wine = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data')
        wine.columns = ['class', 'alcohol', 'malic_acid', 'ash', 'alcalinity_of_ash', 'magnesium',
                        'total_phenols', 'flavanoids', 'nonflavanoid_phenols', 'proanthocyanins',
                        'color_intensity', 'hue', 'dilution', 'proline']
        wine['index'] = np.arange(len(wine))
        wine.set_index('index', inplace=True)
        pangres.upsert(engine=engine, df=wine, schema='public', table_name='wine', if_row_exists='update')
    else:
        logging.info('Skipping flights table creation')
