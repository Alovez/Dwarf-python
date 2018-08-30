"""
 * Created by alovez on 2018/8/26
"""
import copy
import random


data_schema = {
    'country': range(10),
    'device': range(2),
    'date': range(30),
    'category': range(50),
    'download': range(10)
}

data = []


def genertate_data(schema, key, line):
    c_dict = {k: v for k, v in schema.iteritems() if k != key}
    for item in schema.get(key):
        c_line = copy.deepcopy(line)
        c_line.append(str(item))
        if len(c_dict) > 0:
            genertate_data(c_dict, c_dict.keys()[0], c_line)
        else:
            data.append(','.join(c_line) + ',%s\n' % random.randint(0, 10))


if __name__ == '__main__':
    genertate_data(data_schema, data_schema.keys()[0], [])
    with open('./data.csv', 'w') as f:
        f.writelines(data)
