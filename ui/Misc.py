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


def rm_file(path):
    if os.path.isdir(path):
        for f in os.listdir(path):
            rm_file(os.path.join(path, f))
        os.removedirs(path)
