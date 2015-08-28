__ALL__= ['Q', 'Cmp', 'format_typed_value']


class _KW:
    LABEL = '_label'
    SKIP = '_skip'
    TAKE = '_take'
    PROPERTIES = '_properties'


def format_typed_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, unicode):
        return value.encode('utf8')
    if isinstance(value, int):
        return '(i,%d)' % value
    if isinstance(value, long):
        return '(l,%d)' % value
    if isinstance(value, float):
        return '(d,%f)' % value
    if value in (True, False):
        return '(b,%r)' % value
    if isinstance(value, (list, tuple)):
        return '(list,(%s))' % ','.join(format_typed_value(sv) for sv in value)
    if isinstance(value, dict):
        return '(map,(%s))' % ','.join('%s=%s' % (sk, format_typed_value(sv))
                                       for sk, sv in dict.viewitems())
    raise ValueError('Unsupported value type')


def _properties_to_string(properties):
    if len(properties) <= 0:
        return ''
    if len(properties) == 1:
        key, comparison, value = properties[0]
        return '[%s,%s,%s]' % (key,comparison,format_typed_value(value)) 
    return '[%s]' % ','.join(_properties_to_string(sp) for sp in properties)


class Cmp:
    LT = '<'
    LTE = '<='
    EQ = '='
    NE = '<>'
    GTE = '>='
    GT = '>'


_COMPARISONS = (Cmp.LT, Cmp.LTE, Cmp.EQ, Cmp.NE, Cmp.GTE, Cmp.GT)
_GREMLIN_COMPARISONS = {
                        Cmp.LT : 'Compare.LESS_THAN',
                        Cmp.LTE : 'Compare.LESS_THAN_EQUAL',
                        Cmp.EQ : 'Compare.EQUAL',
                        Cmp.NE : 'Compare.NOT_EQUAL',
                        Cmp.GTE : 'Compare.GREATER_THAN_EQUAL',
                        Cmp.GT : 'Compare.GREATER_THAN'
                        }

class _Q(object):
    def __init__(self, _skip = None, _take = None, _label = None, _properties = [], **kwargs):
        self._skip = _skip
        self._take = _take
        self._label = _label
        self._properties = _properties
        if not self._properties:
            self._properties = [(k, Cmp.EQ, v) for k, v in kwargs.viewitems()]

    def __and__(self, other):
        return _Q(other._skip if self._skip is None else self._skip,
                  other._take if self._take is None else self._take,
                  other._label if self._label is None else self._label,
                  self._properties + other._properties)

    def build(self):
        result = {}
        if not self._skip is None:
            result[_KW.SKIP] = self._skip
        if not self._take is None:
            result[_KW.TAKE] = self._take
        if not self._label is None:
            result[_KW.LABEL] = self._label
        if len(self._properties) > 0:
            result[_KW.PROPERTIES] = _properties_to_string(self._properties)
        return result

    def build_gremlin(self):
        res = '.'.join('has("%s",%s,%r)' % (k, _GREMLIN_COMPARISONS[comparison], v)
                       for k, comparison, v in self._properties)
        if not self._label is None:
            res = '.'.join(['has("label", "%s")' % self._label, res])
        if not (self._skip is None and self._take is None):
            start = self._skip if not self._skip is None else 0
            end = (start + self._take - 1) if not self._take is None else -1
            res += '[%d..%d]' % (start, end)
        return res

def Q(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], _Q):
        return args[0]
    return _Q(*args, **kwargs)
