import copy
SPECIAL_KEY = '*'


class Filters(object):
    def __init__(self, filter_list):
        self.filter_list = filter_list

    def shift(self):
        if len(self.filter_list):
            result = self.filter_list[0]
            self.filter_list = self.filter_list[1:]
        else:
            result = None
        return result

    def __get__(self, obj, objtype):
        return self.filter_list

    def __len__(self):
        return len(self.filter_list)


class Node(object):
    def __init__(self, cells):
        self.cells = cells
        self.closed = False
        if list(cells.itervalues()) and isinstance(list(cells.itervalues())[0], Node):
            self.is_leaf = False
        else:
            self.is_leaf = True

    def set_special(self, value):
        self.cells[SPECIAL_KEY] = value
        self.closed = True

    def close(self):
        if self.is_leaf and not self.closed:
            self.set_special(sum([x for x in self.cells.itervalues()]))
        return self.is_leaf

    def merge_node(self, node):
        self.cells.update(node.cells)
        self.closed = self.closed and node.closed
        self.is_leaf = self.is_leaf and node.is_leaf

    def get_leaves(self):
        leaves = []
        if self.is_leaf:
            return [self]
        else:
            for node in self.cells.itervalues():
                leaves.extend(node.get_leaves())
            return leaves

    def get_value(self, filters):
        if filters:
            key = filters.shift()
        else:
            key = SPECIAL_KEY
        value = self.cells.get(key, '')
        if isinstance(value, Node):
            return value.get_value(filters)
        else:
            return value

    def get_sub_node(self, filters):
        key = filters.shift()
        if len(filters) > 0:
            next_node = self.cells.get(key)
            if isinstance(next_node, Node):
                return next_node.get_sub_node(filters)
            else:
                return None
        elif key is not None:
            return self.cells.get(key)
        else:
            return self

    def is_sub_nodes_closed(self):
        if self.is_leaf:
            return self.closed
        else:
            for node in self.cells.itervalues():
                if not node.closed:
                    return False
            return True

    def get_open_node(self, node_list):
        for node in self.cells.itervalues():
            if not node.close():
                node_list.append(node)
                node.get_open_node(node_list)
        return node_list


def calculate_aggr(to_merge):
    return sum(to_merge)


# def get_key_set(home_node):
#     key_list = []
#     for node in home_node.cells.itervalues():
#         key_list.extend(node.cells.keys())
#     # key_list = list(set(home_node.cells.keys()))
#     key_list = list(set(key_list))
#     if SPECIAL_KEY in key_list:
#         key_list.remove(SPECIAL_KEY)
#     return sorted(key_list)


# def suffix_coalesce(top_node, input_dwarfs):
#     # if top_node.closed:
#     #     return top_node
#     if len(input_dwarfs) == 1:
#         if not top_node.closed:
#             top_node.cells[SPECIAL_KEY] = input_dwarfs[0]
#             top_node.closed = True
#         return input_dwarfs[0]
#     special_cell = {}
#     for input_dwarf in input_dwarfs:
#         key_set = get_key_set(top_node)
#         for key_min in key_set:
#             to_merge = [sub_node.cells[key_min] for sub_node in top_node.cells.itervalues() if sub_node.cells.get(key_min)]
#             if input_dwarf.is_leaf:
#                 special_cell[key_min] = calculate_aggr(to_merge)
#             else:
#                 special_cell[key_min] = suffix_coalesce(input_dwarf, to_merge)
#     if not top_node.closed:
#         special_node = Node(special_cell)
#         if not special_node.is_leaf:
#             write_special_of_leaves(special_node)
#             special_node = suffix_coalesce(special_node, list(special_node.cells.itervalues()))
#         else:
#             special_node.close()
#         top_node.cells[SPECIAL_KEY] = special_node
#         top_node.closed = True
#     return top_node

def get_key_set(input_dwarfs):
    key_list = []
    for dwarf in input_dwarfs:
        key_list.extend(dwarf.cells.keys())
    key_list = list(set(key_list))
    if SPECIAL_KEY in key_list:
        key_list.remove(SPECIAL_KEY)
    return sorted(key_list)


def unprocessed_cells_exist(input_dwarfs):
    for dwarf in input_dwarfs:
        if not dwarf.is_sub_nodes_closed():
            return True
        # if not dwarf.closed:
        #     return True
    return False


def suffix_coalesce(input_dwarfs):
    if len(input_dwarfs) == 1:
        return input_dwarfs[0]
    special_cell = {}
    while unprocessed_cells_exist(input_dwarfs) or len(special_cell) == 0:
        key_set = get_key_set(input_dwarfs)
        for key_min in key_set:
            to_merge = [sub_node.cells[key_min] for sub_node in input_dwarfs if sub_node.cells.get(key_min)]
            if input_dwarfs[0].is_leaf:
                special_cell[key_min] = calculate_aggr(to_merge)
            else:
                special_cell[key_min] = suffix_coalesce(to_merge)
    special_node = Node(special_cell)
    if not special_node.close():
        special_node.set_special(suffix_coalesce(list(special_node.cells.itervalues())))
    return special_node


def get_data_list():
    data_list = []
    with open('./data.csv') as f:
        for l in f.readlines():
            if 'Store' in l:
                continue
            data_list.append(l.replace('\n', '').split(','))

    return data_list


def create_first_tuple(current_tuple):
    current_tuple = copy.deepcopy(current_tuple)
    value = int(current_tuple.pop())
    key = current_tuple.pop()
    node = Node({key: value})
    while current_tuple:
        k = current_tuple.pop()
        current_node = Node({k: node})
        node = current_node
    return node


def get_prefix(current_tuple, last_tuple):
    prefix = []
    for c, l in zip(current_tuple, last_tuple):
        if c == l:
            prefix.append(c)
        else:
            break
    return prefix


def is_new_close_nodes_exist(home_node, prefix, current_tuple):
    if home_node.is_leaf:
        return False
    for key in home_node.cells.keys():
        if key != current_tuple[len(prefix)]:
            if not home_node.cells[key].is_sub_nodes_closed():
                return True
    return False


def create_new_nodes(home_node, current_tuple, prefix):
    current_tuple = copy.deepcopy(current_tuple)
    current_node = home_node
    need_create = [x for x in current_tuple if x not in prefix]
    value = int(need_create.pop())
    key = need_create.pop()
    node = Node({key: value})
    while need_create:
        k = need_create.pop()
        new_node = Node({k: node})
        node = new_node
    current_node.merge_node(node)


def write_special_of_leaves(home_node):
    leaves = home_node.get_leaves()
    for leaf in leaves:
        leaf.close()


def create_data_model():
    data_list = get_data_list()
    last_tuple = data_list.pop()
    root = create_first_tuple(last_tuple)
    while len(data_list):
        current_tuple = data_list.pop()
        prefix = get_prefix(current_tuple, last_tuple)
        home_node = root.get_sub_node(Filters(prefix))
        if is_new_close_nodes_exist(home_node, prefix, current_tuple):
            write_special_of_leaves(home_node)
            if not home_node.is_sub_nodes_closed():
                for new_close_node in home_node.cells.itervalues():
                    if not new_close_node.closed:
                        new_close_node.set_special(suffix_coalesce(list(new_close_node.cells.itervalues())))
        create_new_nodes(home_node, current_tuple, prefix)
        last_tuple = current_tuple
    write_special_of_leaves(root)
    all_open_node = []
    all_open_node = root.get_open_node(all_open_node)
    for node in all_open_node:
        node.set_special(suffix_coalesce(list(node.cells.itervalues())))
    root.set_special(suffix_coalesce(list(root.cells.itervalues())))
    return root


if __name__ == '__main__':
    root = create_data_model()
    while True:
        Store = raw_input("Store: ")
        Customer = raw_input("Customer: ")
        Product = raw_input("Product: ")
        f = Filters([Store, Customer, Product])
        r = root.get_value(f)
        print r
