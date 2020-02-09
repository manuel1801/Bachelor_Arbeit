import requests
import json
import os
import pexpect


class SSHConnect:
    def __init__(self, dev_key='OENDQjg2ODktNUU5Qy00MUI2LThBMUYtRkE0MjdBMkE2Mzky'):
        self.developer_key = dev_key
        self.token = None
        self.public_ip = requests.get('https://api.ipify.org').text

    def login(self, remote_it_user='manuel.barkey@gmail.com', remote_it_pw='hiworld'):
        headers = {
            "developerkey": self.developer_key
        }
        body = {
            "password": remote_it_pw,
            "username": remote_it_user
        }
        url = "https://api.remot3.it/apv/v27/user/login"
        log_resp = requests.post(url, data=json.dumps(body), headers=headers)
        log_resp = log_resp.json()

        if log_resp['status'] == 'false':
            print('wrong remote.it user name or password')
            return False
        else:
            self.token = log_resp['token']
            return True

    def get_device_adress(self, device_name='ssh-Pc'):

        if not self.token:
            return None

        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }
        url = "https://api.remot3.it/apv/v27/device/list/all"
        dev_resp = requests.get(url, headers=headers)
        dev_resp = dev_resp.json()
        for device in dev_resp['devices']:
            if device['devicealias'] == device_name:
                return device['deviceaddress']
        print('Device: ', device_name, ' not Exist')
        return None

    def connect(self, device_address):
        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }
        body = {
            "deviceaddress": device_address,
            "wait": "true",
            "hostip": self.public_ip
        }

        url = "https://api.remot3.it/apv/v27/device/connect"

        conn_resp = requests.post(url, data=json.dumps(body), headers=headers)
        conn_resp = conn_resp.json()

        if conn_resp['status'] == 'false':
            return False

        server, port = conn_resp['connection']['proxy'].split(
            '//')[1].split(':')

        connectionid = conn_resp['connectionid']

        return server, port, connectionid

    def disconnect(self, address, conn_id):
        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }
        body = {
            "deviceaddress": address,
            "connectionid": conn_id
        }

        url = "https://api.remot3.it/apv/v27/device/connect/stop"

        response = requests.post(url, data=json.dumps(body), headers=headers)
        response_body = response.json()

    def send(self, server, port, user, password, file, path):
        command = 'scp -o StrictHostKeyChecking=no -P {} {} {}@{}:{}'.format(
            port, file, user, server, path)

        try:
            child = pexpect.spawn(command)
            r = child.expect(
                ["{}@{}'s password:".format(user, server), pexpect.EOF])
            if r == 0:
                child.sendline(password)
                child.expect(pexpect.EOF)
            elif r == 1:
                print('end of file')
            return True
        except Exception as e:
            print(e)
            return False

    # def send_with_module(server, port, user, password, file, path):
    #     try:
    #         client = paramiko.SSHClient()
    #         client.load_system_host_keys()
    #         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #         client.connect(server, port, user, password)
    #         with SCPClient(client.get_transport()) as scp:
    #             scp.put(file, path)
    #         print('succesfully send with python')
    #     except Exception as e:
    #         print(e)


def main():

    conn = SSHConnect()
    conn.login()
    addr = conn.get_device_adress(device_name='ssh-Pi')
    server, port, con_id = conn.connect(addr)
    print(addr)
    print(server, port, con_id)
    conn.send(server, port, 'pi', 'hiworld', '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test.jpg',
              '/home/pi/Bachelor_Arbeit/Connection/remote_it/received')
    conn.disconnect(addr, con_id)


if __name__ == "__main__":
    main()
