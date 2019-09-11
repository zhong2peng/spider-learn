
def stringlike(obj):
    return isinstance(obj, (str, bytes))

def extend(tag, iterable):
    '''given a tag, extend it in-place with iterable; this works as you would expect
even if iterable contains strings. returns back same tag, modified.'''
    if stringlike(tag):
        raise TypeError('`tag` argument must be Element')
    last_child = tag[-1] if len(tag) else None
    for x in iterable:
        if isinstance(x, (str, bytes)):
            if last_child is None:
                text = tag.text
                tag.text = text+x if text else x
            else:
                tail = last_child.tail
                last_child.tail = tail+x if tail else x
        else:
            tag.append(x)
            last_child = x
    return tag

def split(tag, *, del_children=True, separate_tails=True):
    '''opposite of extend

for example, `split(E"<a>A<child>B</child>C</a>")` will return
`["A", E"<child>B</child>", "C"]`

if `del_children` is true, `del tag[:]` is performed before returning

if `separate_tails` is false, then we don't separate children's text tails,
e.g. `split(E"<a>A<child>B</child>C</a>")` will return
`["A", E"<child>B</child>C"]`
'''
    r = []
    if isinstance(tag, (str, bytes)):
        return r
    append = r.append
    tag_text = tag.text
    tag.text = None
    if tag_text is not None:
        append(tag_text)
    if separate_tails:
        for child in tag:
            child_tail = child.tail
            child.tail = None
            append(child)
            if child_tail is not None:
                append(child_tail)
    else:
        r.extend(tag)
    if del_children:
        del tag[:]
    return r

def unwrap(tag, *, del_children=True, separate_tails=True):
    r = split(
        tag, del_children=del_children, separate_tails=separate_tails)
    if not stringlike(tag):
        tail = tag.tail
        if tail:
            r.append(tail)
    return r

def extend_with_children_of(target, source):
    return extend(target, unwrap(source, separate_tails=False))

def regex_sub_str_iter(regex, string, repl):
    i = 0
    for m in regex.finditer(string):
        k0, k1 = m.span(0)
        if i != k0: yield string[i:k0]
        yield from repl(m)
        i = k1
    k0 = len(string)
    if i != k0: yield string[i:k0]

def regex_sub_e_iter(regex, repl, e):
    if isinstance(e, (str, bytes)):
        yield from regex_sub_str_iter(regex, e, repl)
    else:
        yield e

def transform_text(tag, *transformations):
    src = split(tag)
    r = []
    for transformation in transformations:
        for x in src:
            if isinstance(x, (str, bytes)):
                r.extend(transformation(x))
            else:
                r.append(x)
        src, r = r, src
        r.clear()
    extend(tag, src)
    return tag

def equal(x, y):
    # TODO: don't use function stack
    # TODO: support list as returned by split
    return (x.tag    == y.tag    and
            x.text   == y.text   and
            x.tail   == y.tail   and
            x.attrib == y.attrib and
            len(x)   == len(y)   and
            all(equal(a, b) for a, b in zip(x, y)))

