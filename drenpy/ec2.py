import boto3 as b3
import pprint
import paramiko
import logging
from time import sleep

logging.basicConfig(level=logging.WARNING)

pp = pprint.PrettyPrinter(depth=6)
ec2 = b3.resource('ec2')
ec2_client = b3.client('ec2')
s3 = b3.client('s3')


class Instance:
    def __init__(self,
                 creation=False,
                 instance_id=None,
                 image_id='ami-0bbe28eb2173f6167',
                 instance_type='t2.micro',
                 key_file=None,
                 security_group_id=None,
                 shell_script=None,
                 shell_path=None,
                 keyfile_location=None,
                 username='ubuntu',
                 volume_size=30):
        self.creation = creation
        self.image_id = image_id
        self.instance_type = instance_type
        self.instance_id = instance_id
        self.key_file = key_file
        self.security_group_id = security_group_id
        self.shell_path = shell_path
        self.shell_script = shell_script
        self.keyfile_location = keyfile_location
        self.username = username
        self.volume_size = volume_size
        self.instance_data = None
        self.private_ip_address = None
        self.public_ip_address = None
        self.public_dns_name = None
        self.ssh = None
        self.stdout = None
        self.stderr = None
        self.last_command = None
        self.state = 'State Not Yet Requested'
        self.is_running = False
        self.ssh_creds = 'Not Yet Stored'

    def login_creds(self):
        self.load()
        self.ssh_creds = f'ssh -i "{self.key_file}.pem" {self.username}@{self.public_dns_name}'
        print(f"GLANCES: {self.public_ip_address}:61208")
        print(self.ssh_creds)

    def terminate(self):
        self.instance_data.terminate()

    def stop(self):
        self.instance_data.stop()

    def start(self):

        if not self.creation:
            self.instance_data = ec2.Instance(self.instance_id)
        self.instance_data.start()
        self.instance_data.wait_until_running()
        self.load()

    def status_update(self):
        self.state = self.instance_data.state
        self.is_running = self.state['Name'] == 'running'
        pp.pprint(self.state)
        return self.is_running

    def command(self, command, verbose=False):
        _, stdout, stderr = self.ssh.exec_command(command)
        stdout = stdout.read().splitlines()
        stderr = stderr.read().splitlines()
        self.last_command = {'stdout': stdout, 'stderr': stderr}
        if verbose:
            pp.pprint(stdout)
            pp.pprint(stderr)
        return stdout, stderr

    def modify_server(self, volume_type='t2.xlarge', start=True):
        self.stop()
        self.instance_data.wait_until_stopped()
        ec2_client.modify_instance_attribute(
            InstanceId=self.instance_id,
            Attribute='instanceType',
            Value=volume_type
        )

        if start:
            self.start()
            self.login_creds()

    def load(self):
        logging.info('Waiting until running.')
        self.instance_data.wait_until_running()
        self.instance_data.load()
        self.private_ip_address = self.instance_data.private_ip_address
        self.public_ip_address = self.instance_data.public_ip_address
        self.public_dns_name = self.instance_data.public_dns_name
        self.instance_id = self.instance_data.instance_id


    def send_file(self, local_path, remote_path):
        ftp_client = self.ssh.open_sftp()
        ftp_client.put(local_path, remote_path)
        ftp_client.close()

    def get_file(self, remote_path, local_path):
        ftp_client = self.ssh.open_sftp()
        ftp_client.get(remote_path, local_path)
        ftp_client.close()

    def start_ssh(self, sleep_time=0, verbose=False):
        for second in range(sleep_time):
            if verbose:
                print(f'sleeping: {second / sleep_time}')
            sleep(1)

        print('Inside start_ssh')
        if self.status_update():
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.public_dns_name,
                             username=self.username,
                             key_filename=self.keyfile_location)
        else:
            print('Cannot connect to server')
            return False

    def stop_ssh(self):
        print('Stopping SSH Connection')
        self.ssh.stop()

    def create_instance(self, verbose=False):
        self.shell_script = open(self.shell_path, "r").read()
        if verbose:
            pp.pprint(self.shell_script)

        instances = ec2.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=self.instance_type,
            KeyName=self.key_file,
            SecurityGroupIds=self.security_group_id,
            UserData=self.shell_script,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': self.volume_size,
                        'VolumeType': 'standard'
                    }
                }
            ]
        )

        self.instance_data = instances[0]

        self.load()

        self.login_creds()
