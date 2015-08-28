import os, glob
from pyarc import ClientBase
from rexster_rest.query import Q, format_typed_value


__ALL__ = ['RexsterClient', 'Dir', 'Q']


class Urls:
    GRAPHS = '/graphs'
    GRAPH = GRAPHS + '/{graph}'
    VERTICES = GRAPH + '/vertices'
    VERTEX = VERTICES + '/{vertex_id}'
    INCIDENT = VERTEX + '/{direction}'
    INCIDENT_CNT = INCIDENT + 'Count'
    INCIDENT_IDS = INCIDENT + 'Ids'
    ADJACENT_E = INCIDENT + 'E'
    EDGES = GRAPH + '/edges'
    EDGE = VERTICES + '/{edge_id}'
    INDICES =  GRAPH + '/indices'
    INDEX = INDICES + '/{index_id}'
    INDEX_CNT = INDEX + '/count'
    KEYS = GRAPH + '/keyindices'
    KEYS_V = KEYS + '/vertex'
    KEYS_E = KEYS + '/edge'
    KEY_V = KEYS_V + '/{key}'
    KEY_E = KEYS_E + '/{key}'
    GREMLIN_G = GRAPH + '/tp/gremlin'
    GREMLIN_V = VERTEX + '/tp/gremlin'
    GREMLIN_E = EDGE + '/tp/gremlin'


class Dir:
    IN = 'in'
    OUT = 'out'
    BOTH = 'both'

_DIRS = frozenset({ Dir.IN, Dir.OUT, Dir.BOTH })


class _ItemGetter(object):
    def __init__(self, base_future, attrib, default = None):
        self.base_future = base_future
        self.attrib = attrib
        self.default = None

    def get(self):
        return self.base_future.get().get(self.attrib, self.default)


class _FirstGetter(object):
    def __init__(self, impl):
        self.impl = impl
    def get(self):
        res = self.impl.get()
        if len(res) > 0:
            return res[0]
        return None


class RexsterClient(ClientBase):
    def __init__(self, base_url, graph, async = False):
        super(RexsterClient, self).__init__(base_url,
                                            default_url_args = { 'graph' : graph },
                                            async = async)
        self.scripts = {}
        self.refresh_scripts(os.path.join(os.path.dirname(__file__), 'scripts'))

    ################################ GET operations ###########################
    def vertices(self, key = None, value = None):
        args = { 'key' : key, 'value' : format_typed_value(value) } if not key is None else {}
        return self.get(Urls.VERTICES, query_args = args)

    def vertex(self, _id):
        return self.get(Urls.VERTEX, url_args = { 'vertex_id' : _id })

    def incident(self, _id, direction, *query_args, **query_kwargs):
        return self._neighbor_impl(Urls.INCIDENT, _id, direction, *query_args, **query_kwargs)

    def count_incident(self, _id, direction, *query_args, **query_kwargs):
        return self._neighbor_impl(Urls.INCIDENT_CNT, _id, direction, *query_args, **query_kwargs)

    def incident_ids(self, _id, direction, *query_args, **query_kwargs):
        return self._neighbor_impl(Urls.INCIDENT_IDS, _id, direction, *query_args, **query_kwargs)

    def edges(self, key = None, value = None):
        args = { 'key' : key, 'value' : format_typed_value(value) } if not key is None else {}
        return self.get(Urls.EDGES, query_args = args)

    def edge(self, _id):
        return self.get(Urls.EDGE, url_args = { 'edge_id' : _id })

    def adjacent_edges(self, _id, direction, *query_args, **query_kwargs):
        return self._neighbor_impl(Urls.ADJACENT_E, _id, direction, *query_args, **query_kwargs)
    
    def indices(self):
        return self.get(Urls.INDICES)
    
    def query_index(self, index, key, value):
        return self._index_impl(Urls.INDEX, index, key, value)
    
    def query_index_cnt(self, index, key, value):
        return self._index_impl(Urls.INDEX_CNT, index, key, value)

    def keys(self):
        return self.get(Urls.KEYS)

    def keys_vertex(self):
        return self.get(Urls.KEYS_V)

    def keys_edge(self):
        return self.get(Urls.KEYS_E)

    def _index_impl(self, url_template, index, key, value):
        return self.get(url_template,
                        url_args = { 'index_id' : index },
                        query_args = { 'key' : key, 'value' : format_typed_value(value) })

    def _neighbor_impl(self, url_template, _id, direction, *query_args, **query_kwargs):
        if not direction in _DIRS:
            raise ValueError('"%s" is not a valid direction (only %s allowed)' % (direction,
                                                                                  ', '.join(_DIRS)))
        return self.get(url_template,
                        url_args = { 'vertex_id' : _id, 'direction' : direction },
                        query_args = Q(*query_args, **query_kwargs).build())

    ############################### POST operations ###########################
    def create_vertex(self, **properties):
        return self.post(Urls.VERTICES, payload = properties)

    def create_vertex_with_known_id(self, _id, **properties):
        return self.post(Urls.VERTEX,
                         url_args = { 'vertex_id' : _id },
                         payload = properties)

    def upsert_vertex(self, _id, **properties):
        return self.post(Urls.VERTEX, url_args = { 'vertex_id' : _id }, payload = properties)

    def create_edge(self, _outV, _inV, _label, **properties):
        payload = {'_outV' : _outV,
                   '_inV' : _inV,
                   '_label' : _label}
        payload.update(properties)
        return self.post(Urls.EDGES, payload = payload)

    def create_edge_with_known_id(self, _id, _outV, _inV, _label, **properties):
        payload = {'_outV' : _outV,
                   '_inV' : _inV,
                   '_label' : _label}
        payload.update(properties)
        return self.post(Urls.EDGES, url_args = { 'edge_id' : _id }, payload = payload)

    def update_edge(self, _id, **properties):
        return self.post(Urls.EDGES, url_args = { 'edge_id' : _id }, payload = properties)

    def create_index(self, index_id, **params):
        params['class'] = 'vertex'
        return self.post(Urls.INDEX, url_args = { 'index_id' : index_id }, payload = params)

    def create_key_index_vertex(self, index_id, key):
        return self.post(Urls.KEY_V, url_args = { 'index_id' : index_id, 'key' : key })

    def create_key_index_edge(self, index_id, key):
        return self.post(Urls.KEY_E, url_args = { 'index_id' : index_id, 'key' : key })

    ############################### PUT operations ###########################
    def update_vertex_put(self, _id, **properties):
        return self.put(Urls.VERTEX, url_args = { 'vertex_id' : _id }, payload = properties)

    def update_edge_put(self, _id, **properties):
        return self.put(Urls.EDGES, url_args = { 'edge_id' : _id }, payload = properties)

    def index_vertex(self, index_id, vertex_id, key, value):
        return self.put(Urls.INDEX,
                        url_args = { 'index_id' : index_id },
                        payload = {'id' : vertex_id,
                                   'key' : key,
                                   'value' : value })

    ############################## DELETE operations ##########################
    def delete_vertex(self, _id):
        return self.delete(Urls.VERTEX, url_args = { 'vertex_id' : _id })

    def delete_vertex_properties(self, _id, *keys):
        return self.delete(Urls.VERTEX, url_args = { 'vertex_id' : _id }, query_args = { k : '' for k in keys })

    def delete_edge(self, _id):
        return self.delete(Urls.EDGE, url_args = { 'edge_id' : _id })

    def delete_edge_properties(self, _id, *keys):
        return self.delete(Urls.EDGE, url_args = { 'edge_id' : _id }, query_args = { k : '' for k in keys })

    def drop_index(self, _id):
        return self.delete(Urls.INDEX, url_args = { 'index_id' : _id })

    def remove_vertex_from_index(self, index_id, vertex_id, key, value):
        return self.delete(Urls.INDEX,
                           url_args = { 'index_id' : index_id },
                           query_args = {'id' : vertex_id,
                                         'key' : key,
                                         'value' : format_typed_value(value),
                                         'class' : 'vertex' })

    ############################### Scripts ###########################
    def refresh_scripts(self, dirname):
        for f in glob.glob(os.path.join(dirname, "*.groovy")):
            self.load_script(f)

    def load_script(self, filename):
        if not os.path.isfile(filename):
            return
        script_name = os.path.splitext(os.path.basename(filename))[0]
        with open(filename, 'r') as f:
            self.scripts[script_name] = f.read()

    def run_script_on_graph(self, script_code_or_name, **params):
        return self.post(Urls.GREMLIN_G, payload = {
                                                    "params" : params,
                                                    "script" : self.scripts.get(script_code_or_name,
                                                                                script_code_or_name)
                                                    })

    def run_script_on_vertex(self, script_code_or_name, vertex_id, **params):
        return self.post(Urls.GREMLIN_V,
                         url_args = { 'vertex_id' : vertex_id },
                         payload = {
                                    "params" : params,
                                    "script" : self.scripts.get(script_code_or_name,
                                                                script_code_or_name)
                                    })

    def run_script_on_edge(self, script_code_or_name, edge_id, **params):
        return self.post(Urls.GREMLIN_E,
                         url_args = { 'edge_id' : edge_id },
                         payload = {
                                    "params" : params,
                                    "script" : self.scripts.get(script_code_or_name,
                                                                script_code_or_name)
                                    })

    def lookup_vertex(self, *query_args, **query_kwargs):
        q_str = Q(*query_args, **query_kwargs).build_gremlin()
        if q_str:
            q_str = 'g.query().%s.vertices()' % q_str
        return self.run_script_on_graph(q_str)

    def get_unique_vertex(self, *query_args, **query_kwargs):
        return _FirstGetter(self.lookup_vertex(*query_args, **query_kwargs))

    def lookup_edge(self, *query_args, **query_kwargs):
        q_str = Q(*query_args, **query_kwargs).build_gremlin()
        if q_str:
            q_str = 'g.E.%s.toList()' % q_str
        return self.run_script_on_graph(q_str)

    def upsert_vertex_custom_id(self, id_prop, id_value, label = None, **props):
        return self.run_script_on_graph('upsert_vertex',
                                        id_prop = id_prop,
                                        id_value = id_value,
                                        label = label,
                                        properties = props)

    ############################## Overrides ##########################
    def do_req(self, *args, **kwargs):
        base_future = super(RexsterClient, self).do_req(*args, **kwargs)
        return _ItemGetter(base_future, 'results')
