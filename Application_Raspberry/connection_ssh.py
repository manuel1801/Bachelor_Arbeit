import requests
import json
import os
import pexpect
from time import sleep


class SSHConnect:
    def __init__(self, dev_key='NEU3RTVFNEMtNjRGRi00MzBFLUIyNTgtOUVFQjRGMjcxOTRB'):
        self.developer_key = dev_key
        self.token = None
        self.device_adress = None
        # self.public_ip = requests.get('https://api.ipify.org').text

    def login(self, remote_it_user='animals.detection@gmail.com', remote_it_pw='animalsdetection', device_name='ssh-Pc', retry=5):
        headers = {
            "developerkey": self.developer_key
        }
        body = {
            "password": remote_it_pw,
            "username": remote_it_user
        }
        url = "https://api.remot3.it/apv/v27/user/login"

        for i in range(retry):
            print('try to login for ' + str(i+1) + '. time')
            try:
                log_resp = requests.post(
                    url, data=json.dumps(body), headers=headers)
                break
            except:
                print('login failed: ' + str(i+1) + '. try')
                if i == retry - 1:
                    return False
            sleep(0.5)

        log_resp = log_resp.json()

        if log_resp['status'] == 'false':
            print('wrong remote.it user name or password')
            return False
        else:
            self.token = log_resp['token']

        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }

        url = "https://api.remot3.it/apv/v27/device/list/all"

        try:
            dev_resp = requests.get(url, headers=headers)
        except:
            print('failed to get device list')
            return False

        dev_resp = dev_resp.json()

        for device in dev_resp['devices']:
            if device['devicealias'] == device_name:
                self.device_adress = device['deviceaddress']
                return True

        print('Device: ', device_name, ' not Exist')
        return False

    def connect(self):
        if not self.token or not self.device_adress:
            print('token or device adress not found. login again')
            return False
        # host_ip = requests.get('https://api.ipify.org').text
        # print('host ip is ', host_ip)
        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }
        body = {
            "deviceaddress": self.device_adress,
            "wait": "true",
            # "hostip": host_ip
            "hostip": None
        }

        url = "https://api.remot3.it/apv/v27/device/connect"
        try:
            conn_resp = requests.post(
                url, data=json.dumps(body), headers=headers)
        except:
            print('conn req failed')
            return False

        conn_resp = conn_resp.json()

        if conn_resp['status'] == 'false':
            print('conn status false')
            return False

        server, port = conn_resp['connection']['proxy'].split(
            '//')[1].split(':')

        connectionid = conn_resp['connectionid']

        return server, port, connectionid

    def disconnect(self, conn_id):
        if not self.device_adress:
            print('no device to disconnect')
            return False

        headers = {
            "developerkey": self.developer_key,
            # Created using the login API
            "token": self.token
        }
        body = {
            "deviceaddress": self.device_adress,
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
                return True
            elif r == 1:
                print('end of file')
                return False

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
    print(conn.public_ip)
    conn.login()
    addr = conn.get_device_adress(device_name='ssh-Pi')
    ret = conn.connect(addr)
    print(ret)
    if ret:
        server, port, con_id = ret

    # print(addr)
    # print(server, port, con_id)
    conn.send(server, port, 'pi', 'animalsdetection', '/home/manuel/Bachelor_Arbeit/Connection/remote_it/test.jpg',
              '/home/pi/Bachelor_Arbeit/Connection/remote_it/received')
    conn.disconnect(addr, con_id)


if __name__ == "__main__":
    main()
