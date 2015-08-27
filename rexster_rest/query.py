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


class _Q(object):
    def __init__(self, _skip = None, _take = None, _label = None, _properties = None, **kwargs):
        self._skip = _skip
        self._take = _take
        self._label = _label
        self._properties = _properties
        if not self._properties is None:
            self._properties = [(k, Cmp.EQ, v) for k, v in kwargs.viewitems()]

    def __and__(self, other):
        return _Q(other._skip if self._skip is None else self._skip,
                  other._take if self._take is None else self._take,
                  other._label if self._label is None else self._label,
                  self._properties + other.properties)

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


def Q(*args, **kwargs):
    if len(args) == 1 and isinstance(args[1], _Q):
        return args[1]
    return _Q(*args, **kwargs)
