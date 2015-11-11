'''
Helper functions that aid in renaming streams and components
and creating data structures that we need to convert from
the Flowhub UI's JSON to my special JSON.

'''


def make_instance_dict(data, instances):
    '''
    make_instance_dict() makes a dict of component names with id
    paired with a dict of streams that go in and out of that
    component instance
    Eg. {component: {'in': [in_stream], 'out': [out_stream]}}

    Parameters
    ----------
    data : dict
        Dict created from a Flowhub UI generated JSON file
        with the key 'connections'

    instances : list
        List of each unique component-with-id name

    Returns
    -------
    instance_dict : dict
        Dict of each unique component-with-id with a
        dict of in and out streams
    '''
    instance_dict = {}
    for i in instances:
        i = i.encode('ascii', 'ignore')
        instance_dict[i] = {'in': [], 'out': []}

    for conn in data['connections']:
        if 'src' in conn.keys():
            sp = conn['src']['process'].encode('ascii', 'ignore')
            spp = conn['src']['port'].encode('ascii', 'ignore')
        else:
            # for constant parameters because they have no 'src'
            sp = 'none'
            spp = conn['tgt']['port'].encode('ascii', 'ignore') +\
                '=' + conn['data']

        tp = conn['tgt']['process'].encode('ascii', 'ignore')
        tpp = conn['tgt']['port'].encode('ascii', 'ignore')

        if sp == 'none':
            instance_dict[tp]['in'].append(spp)
        else:
            if sp + '_' + spp not in instance_dict[sp]['out']:
                instance_dict[sp]['out'].append(sp + '_' + spp)

            instance_dict[tp]['in'].append(sp + '_' + spp)
    return instance_dict


def cast(s):
    '''
    cast() automatically converts a str to the
    object type associated with its value
    (float, int or str)

    Parameters
    ----------
    s : str
        String of possibly a number

    Returns
    -------
    s : int/float/str
        Same thing as input arg but as the appropriate
        object type
    '''
    try:
        int(s)
        return float(s)
    except ValueError:
        try:
            float(s)
            return int(s)
        except ValueError:
            return str(s)


def clean_id(component):
    '''
    clean_id() splits and returns the component name with id
    in two strings

    Parameters
    ----------
    component : str
        Component names with random id

    Returns
    -------
    label : str
        Plain component name with no id

    cid : str
        The id that was appended to the component

    '''
    if '_' not in component:
        return component, ''

    l_array = component.split('_')
    l = len(l_array) - 1
    cid = l_array[l]
    label = str()
    for i in range(0, l):
        label = label + l_array[i] + '_'
    label = label[:-1]

    return label, cid


def make_comp_list(instance_dict):
    '''
    make_comp_list() creates a dict used for replacing
    the random 4 or 5 char id associated with each
    instance of a component with a shorter integer in
    name_with_new_id()

    Parameters
    ----------
    instance_dict : dict
        Component names with random id's paired with
        dict of it's 'in' and 'out' ports

    Returns
    -------
    comp_list : dict
        Plain component name paired with list of id's
        associated with it

    '''
    comp_list = dict()
    for component, connections in instance_dict.items():
        label, cid = clean_id(component)
        label = label.split('/')[1]
        if label in comp_list.keys():
            comp_list[label].append(cid)
        else:
            comp_list[label] = [cid]

    return comp_list


def name_with_new_id(comp_list, name, id):
    '''
    name_with_new_id() replaces a component name,
    if there are multiple instances of it,
    with the random id with an integer (1, 2, 3,...)
    based on the index of the random id in
    comp_list.

    Parameters
    ----------
    comp_list : dict
        Dict of each component name paired with
        list of id's associated with it

    name : str
        Plain component name

    id: str
        Random id attached to component name

    Returns
    -------
    name : str
        Component name appended with new integer id

    '''
    new_name = name
    if name not in comp_list.keys():
        return new_name
    elif comp_list[name].index(id) > 0:
        new_name = name + str(comp_list[name].index(id))
        return new_name
    return new_name
