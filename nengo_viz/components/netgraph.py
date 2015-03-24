import time
import struct

import numpy as np
import nengo
import json

from nengo_viz.components.component import Component

class Config(nengo.Config):
    def __init__(self):
        super(Config, self).__init__()
        for cls in [nengo.Ensemble, nengo.Node]:
            self.configures(cls)
            self[cls].set_param('pos', nengo.params.Parameter(None))
            self[cls].set_param('size', nengo.params.Parameter(None))
        self.configures(nengo.Network)
        self[nengo.Network].set_param('pos', nengo.params.Parameter(None))
        self[nengo.Network].set_param('size', nengo.params.Parameter(None))
        self[nengo.Network].set_param('expanded', nengo.params.Parameter(False))


class NetGraph(Component):
    configs = {}

    def __init__(self, viz, config=None):
        super(NetGraph, self).__init__(viz)
        self.viz = viz
        if config is None:
            config = NetGraph.configs.get(self.viz.model, None)
            if config is None:
                config = Config()
                NetGraph.configs[self.viz.model] = config
        self.config = config
        self.to_be_expanded = [self.viz.model]
        self.uids = {}

    def update_client(self, client):
        if len(self.to_be_expanded) > 0:
            self.viz.viz.lock.acquire()
            network = self.to_be_expanded.pop(0)
            self.expand_network(network, client)
            if network is self.viz.model:
                self.send_pan_and_zoom(client)
            self.viz.viz.lock.release()
        else:
            pass

    def javascript(self):
        return 'new VIZ.NetGraph({parent:main, id:%(id)d});' % dict(id=id(self))

    def message(self, msg):
        info = json.loads(msg)
        action = info.get('act', None)
        if action is not None:
            del info['act']
            getattr(self, 'act_' + action)(**info)
        else:
            print 'received message', msg

    def act_expand(self, uid):
        net = self.uids[uid]
        self.to_be_expanded.append(net)
        self.config[net].expanded = True

    def act_collapse(self, uid):
        net = self.uids[uid]
        self.config[net].expanded = False

    def act_pan(self, x, y):
        print 'pan to', x, y
        self.config[self.viz.model].pos = x, y

    def act_zoom(self, scale, x, y):
        print 'zoom to', scale
        self.config[self.viz.model].size = scale, scale
        self.config[self.viz.model].pos = x, y

    def act_pos(self, uid, x, y):
        obj = self.uids[uid]
        self.config[obj].pos = x, y

    def act_size(self, uid, width, height):
        obj = self.uids[uid]
        self.config[obj].size = width, height

    def expand_network(self, network, client):
        if network is self.viz.model:
            parent = None
        else:
            parent = self.viz.viz.get_uid(network)
        for ens in network.ensembles:
            self.create_object(client, ens, type='ens', parent=parent)
        for node in network.nodes:
            self.create_object(client, node, type='node', parent=parent)
        for net in network.networks:
            self.create_object(client, net, type='net', parent=parent)
        for conn in network.connections:
            self.create_connection(client, conn, parent=parent)
        self.config[network].expanded = True

    def create_object(self, client, obj, type, parent):
        pos = self.config[obj].pos
        if pos is None:
            import random
            pos = random.uniform(0, 1), random.uniform(0, 1)
            self.config[obj].pos = pos
        size = self.config[obj].size
        if size is None:
            size = (0.1, 0.1)
            self.config[obj].size = size
        label = self.viz.viz.get_label(obj)
        uid = self.viz.viz.get_uid(obj)
        self.uids[uid] = obj
        info = dict(uid=uid, label=label, pos=pos, type=type, size=size,
                    parent=parent)
        if type == 'net':
            info['expanded'] = self.config[obj].expanded
        client.write(json.dumps(info))

    def send_pan_and_zoom(self, client):
        pan = self.config[self.viz.model].pos
        if pan is None:
            pan = 0, 0
        zoom = self.config[self.viz.model].size
        if zoom is None:
            zoom = 1.0
        else:
            zoom = zoom[0]
        client.write(json.dumps(dict(type='pan', pan=pan)))
        client.write(json.dumps(dict(type='zoom', zoom=zoom)))

    def create_connection(self, client, conn, parent):
        pre = self.viz.viz.get_uid(conn.pre_obj)
        post = self.viz.viz.get_uid(conn.post_obj)
        uid = 'conn_%d' % id(conn)
        self.uids[uid] = conn
        info = dict(uid=uid, pre=pre, post=post, type='conn', parent=parent)
        client.write(json.dumps(info))



