# https://docs.google.com/document/d/1SyPowrIkrgEG4v3cTlpjbyyxWQ6AQMttnDREiMRnLus/edit
import logging
import pprint
from dotenv import load_dotenv
from drenpy.dbutils import load_tables
from drenpy.docker import start_docker, stop_docker
from drenpy.aws import list_buckets, run_aws_shit


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # Project Level Configurations
    run_aws_shit(
        instance_type='p2.xlarge',
        image_id='ami-03fd79b69af5903ca',
        key_file='fdren',
        username='ubuntu',
        keyfile_location='/Users/fdrennan/fdren.pem',
        security_group_ids=['sg-0bec91fe0dd33d512'],
        # user_data=open("shell/instance.sh", "r").read(),
        user_data=open("shell/instance_deep_learning.sh", "r").read(),
        terminate=True
    )


    # load_dotenv()
    # pp = pprint.PrettyPrinter(depth=6)
    # RUN_DOCKER = True
    #
    # # Create AWS Configurations
    # list_buckets()
    #
    # # Run Docker if needed
    # if RUN_DOCKER:
    #     logging.info('Starting Docker')
    #     start_docker()
    #
    # load_tables()
    #
    # # Stopping Docker if needed
    # if RUN_DOCKER:
    #     logging.info('STOPPING DOCKER')
    #     # stop_docker()
