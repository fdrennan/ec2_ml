import os
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

def start_docker():
    print(os.getenv("DRENPY_HOME"))
    logging.info('Building your dockerfile')
    subprocess.run(['docker', 'build', '-t', 'drenpy', '--file', './Dockerfile', '.'])
    airflow_path = os.path.join(os.getenv("DRENPY_HOME"), 'airflow/docker-compose.yaml')
    logging.info('Starting Docker Compose')
    subprocess.run(['docker-compose', '-f', airflow_path, 'up', '-d', '--build', 'drenpy_postgres'])
    subprocess.run(['docker-compose', '-f', airflow_path, 'up', '-d', '--build', 'drenpy_initdb'])
    subprocess.run(['docker-compose', '-f', airflow_path, 'up', '-d', '--force-recreate'])


def stop_docker():
    airflow_path = os.path.join(os.getenv("DRENPY_HOME"), 'airflow/docker-compose.yaml')
    logging.info('Shutting down docker compose')
    subprocess.run(['docker-compose', '-f', airflow_path, 'down'])
