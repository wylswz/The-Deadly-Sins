import json
import requests, getpass
import os
import datetime


class CouchAgent:
    def __init__(self, host, port=5984, username=None, password=None, name='unknown'):
        if username is None:
            self.username = input("Username for {0}: ".format(name))
        else:
            self.username = username
        if password is None:
            self.password = getpass.getpass()
        else:
            self.password = password
        self.host = host
        self.name = name
        self.port = port
        self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }


    def init_db(self):
        """
        Create some initial databases
        :return:
        """
        username = self.username
        password = self.password
        resp = requests.put(
            'http://{2}:{3}@{0}:{1}/database'.format(self.host, self.port, username, password)
        )
        print("[Setting up]: Creating user database...")
        requests.put(
            'http://{2}:{3}@{0}:{1}/_users'.format(self.host, self.port, username, password)
        )

        print("[Setting up]: Creating replicator database...")
        requests.put(
            'http://{2}:{3}@{0}:{1}/_replicator'.format(self.host, self.port, username, password)
        )
        print("[Setting up]: Creating global change database...")
        requests.put(
            'http://{2}:{3}@{0}:{1}/_global_changes'.format(self.host, self.port, username, password)
        )

        return resp

    def enable_cluster(self):
        username = self.username
        password = self.password
        resp = requests.post(
            'http://{0}:{1}@{2}:{3}/_cluster_setup'.format(username, password, self.host, self.port),
            json={
                "action": "enable_cluster",
                "bind_address": "0.0.0.0",
                "username": username,
                "password": password,
                "node_count": "3"
            },
            headers = self.headers
        )
        return resp

    def disable_cluster(self):
        """
        Change to standalone mode
        :return:
        """
        username = self.username
        password = self.password
        resp = requests.post(
            'http://{0}:{1}@{2}:{3}/_cluster_setup'.format(username, password, self.host, self.port),
            json={
                "action": "enable_single_node",
                "bind_address": "0.0.0.0",
                "username": username,
                "password": password,
            },
            headers = self.headers
        )
        return resp

    def uuid_setup(self):
        """
        Set up unique id for node
        :return:
        """
        username = self.username
        password = self.password

        resp = requests.get(
            'http://{0}:{1}/_uuids'.format(self.host, self.port),
            params={
                "count": 2
            }
        )

        uuids = json.loads(resp.content)['uuids']
        print(uuids)
        requests.put(
            'http://{2}:{3}@{0}:{1}/_node/_local/_config/couchdb/uuid'.format(self.host, self.port, username, password),
            data=uuids[0]
        )

        requests.put(
            'http://{2}:{3}@{0}:{1}/_node/_local/_config/couch_httpd_auth/secret'.format(self.host, self.port, username,
                                                                                        password),
            data=uuids[1]
        )

    def init_join(self,  remote_host, remote_port=5984):
        """
        Enable cluster mode for nodes
        :param remote_host:
        :param remote_port:
        :return:
        """
        username = self.username
        password = self.password

        remote_username = input("Remote username")
        remote_password = getpass.getpass("Remote password")
        resp = requests.post(
            'http://{0}:{1}@{2}:{3}/_cluster_setup'.format(username, password, self.host, self.port),
            json={
                "action": "enable_cluster",
                "bind_address": "0.0.0.0",
                "username": username,
                "password": password,
                "port": remote_port,
                "node_count": "3",
                "remote_node": remote_host,
                "remote_current_user": remote_username,
                "remote_current_password": remote_password
            },
            headers=self.headers

        )
        return resp

    def join_node(self, remote_host, remote_port=5984):
        """
        Join a node to cluster
        :param remote_host:
        :param remote_port:
        :return:
        """
        username = self.username
        password = self.password

        remote_username = input("Remote username")
        remote_password = getpass.getpass("Remote password")

        resp = requests.post(
            'http://{0}:{1}@{2}:{3}/_cluster_setup'.format(username, password, self.host, self.port),
            json={
                "action": "add_node",
                "host": remote_host,
                "port": remote_port,
                "username": remote_username,
                "password": remote_password
            },
            headers=self.headers
        )
        return resp

    def finalize_cluster(self):
        username = self.username
        password = self.password
        resp = requests.post(
            'http://{0}:{1}@{2}:5984/_cluster_setup'.format(username, password, self.host),
            json={
                "action": "finish_cluster"
            },
            headers=self.headers

        )
        return resp

    def create_user(self, username, password, roles=[], type='user'):
        resp = requests.put(
            'http://{0}:{1}/_users/org.couchdb.user:{2}'.format(self.host, self.port, username),
            data=json.dumps(
                {
                    "name": username,
                    "password": password,
                    "roles": roles,
                    "type": type
                }
            ),
            headers=self.headers

        )

        return resp




if __name__ == "__main__":
    resp = {}
    config_file = 'N/A'
    print("Please give username and password for the dbs(Default to be unified: )")
    username = input("Remote username")
    password = getpass.getpass("Remote password")
    # master = '45.113.233.243'
    slave1 = '45.113.233.243'
    slave2 = '45.113.235.196'
    slave3 = '45.113.233.232'

    # agent = CouchAgent(master, name='master', username='admin', password='123qweasd')
    slave_agent_1 = CouchAgent(slave1, name='slave1', username=username, password=password)
    slave_agent_2 = CouchAgent(slave2, name='slave2', username=username, password=password)
    slave_agent_3 = CouchAgent(slave3, name='slave3', username=username, password=password)

    # agent.init_db()
    #slave_agent_1.init_db()
    #slave_agent_2.init_db()
    #slave_agent_3.init_db()

    # resp = agent.join_node_to(remote_host=master)
    #slave_agent_1.uuid_setup()
    #slave_agent_2.uuid_setup()
    #slave_agent_3.uuid_setup()

    #slave_agent_1.init_join(remote_host=slave1)
    #slave_agent_1.init_join(remote_host=slave2)
    #slave_agent_1.init_join(remote_host=slave3)

    # resp = slave_agent_1.join_node(remote_host=slave1)
    resp = slave_agent_1.join_node(remote_host=slave2)
    resp = slave_agent_1.join_node(remote_host=slave3)

    #resp = slave_agent_1.finalize_cluster()

    #print(resp.content)
