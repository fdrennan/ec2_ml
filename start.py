from drenpy.ec2 import Instance
import logging


def instance_stop(server_object):
    logging.info('Stopping the Instance')
    server_object.stop()


if __name__ == '__main__':
    # FREQUENTLY CHANGED PARAMETERS
    model_name = 'tf.py'
    update_docker = False
    invalidate_cache_docker = True
    shell_script_name = 'instance_deep_learning.sh'

    # LESS FREQUENTLY CHANGED PARAMETERS
    instance_id = 'i-074e161d01f09c4ea'
    key_file = 'fdren'
    keyfile_location = f'/Users/fdrennan/{key_file}.pem'

    # LOCAL FILE PATHS
    script_path_local = f'shell/{shell_script_name}'
    python_path_local = f'scripts/{model_name}'

    # REMOTE FILE PATHS
    script_path_remote = f'/home/ubuntu/{shell_script_name}'
    python_path_remote = f'/home/ubuntu/{model_name}'

    # START THE SERVER
    server = Instance(
        instance_id=instance_id,
        key_file=key_file,
        keyfile_location=keyfile_location,
        # image_id='ami-03fd79b69af5903ca',  # My Pre-Built Tensorflow GPU Image
        # instance_type='p2.xlarge',
        # shell_script="shell/instance_deep_learning.sh",
        # security_group_id=['sg-0bec91fe0dd33d512']
    )

    server.start()
    server.start_ssh(sleep_time=45, verbose=True)
    print('Login Parameters')
    print(server.login_creds())

    if update_docker:
        server.send_file('requirements.txt.tensorflow', '/home/ubuntu/requirements.txt')
        server.send_file('Dockerfile', '/home/ubuntu/Dockerfile')
        server.send_file(script_path_local, script_path_remote)
        logging.info('Building Dockerfile')
        if invalidate_cache_docker:
            server.command("/usr/bin/docker build -t tensordren --file ./Dockerfile . --no-cache")
        else:
            server.command("/usr/bin/docker build -t tensordren --file ./Dockerfile .")

    server.send_file(python_path_local, python_path_remote)
    # MAKE A MODEL
    print('Login Parameters')
    print(server.login_creds())
    server.command(f"docker run --gpus all -t -v $(pwd):/root  tensordren python /root/{model_name}")
    # docker logs --tail=0 --follow
    # docker-compose logs --tail=0 --follow

    # server.stop()
