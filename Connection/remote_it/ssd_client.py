import paramiko
from scp import SCPClient

file = open('test.jpg', 'rb').read()


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


ssh = createSSHClient('proxy50.rt3.io', '36270', 'pi', 'hiworld')

with SCPClient(ssh.get_transport()) as scp:
    scp.put('test.jpg')
