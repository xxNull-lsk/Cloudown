import os


def size2string(size_bytes):
    if isinstance(size_bytes, str):
        size_bytes = int(size_bytes)

    if size_bytes < 1024:
        return "%d B" % size_bytes

    curr = size_bytes / 1024.0
    if curr < 1024:
        return "%.2f KB" % curr
    curr = curr / 1024.0
    if curr < 1024:
        return "%.2f MB" % curr
    curr = curr / 1024.0
    return "%.2f GB" % curr


def choking2string(choking):
    if choking == 'true':
        return '阻塞'
    else:
        return '正常'


def rm_dir(path):
    if os.path.isdir(path):
        for f in os.listdir(path):
            rm_dir(os.path.join(path, f))
        os.removedirs(path)
    else:
        os.unlink(path)


def merged_dict(dict1, dict2):
    for v in dict2:
        if isinstance(dict2[v], dict):
            merged_dict(dict1[v], dict2[v])
        else:
            dict1[v] = dict2[v]
