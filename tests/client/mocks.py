# -*- coding: utf-8 -*

from copy import deepcopy

tree = {
    '.': [
        ['bar_dir', 'baz_dir', 'foo_dir'],
        ['hello_world.py', 'README.md'],
    ],
    './bar_dir': [
        ['bar_dir_2'],
        ['bar_data.h5'],
    ],
    './bar_dir/bar_dir_2': [
        ['bar_dir_3'],
        ['bar_file.py'],
    ],
    './bar_dir/bar_dir_2/bar_dir_3': [
        [],
        ['bar_data.h5'],
    ],
    './baz_dir': [
        ['baz_dir_2'],
        [],
    ],
    './baz_dir/baz_dir_2': [
        ['baz_dir_3'],
        ['baz_file.md', 'baz_file.txt'],
    ],
    './baz_dir/baz_dir_2/baz_dir_3': [
        [], [],
    ],
    './foo_dir': [
        [],
        ['foo_file.py'],
    ],
}


def mock_fs1(*args):
    """
    This returns an array that mocks what os.walk() would return when walking
    the following file system:
    .
    ├── bar_dir
    │   ├── bar_data.h5
    │   └── bar_dir_2
    │       └── bar_dir_3
    │           └── bar_data.h5
    │       └── bar_file.py
    ├── baz_dir
    │   └── baz_dir_2
    │       ├── baz_dir_3
    │       ├── baz_file.md
    │       └── baz_file.txt
    ├── foo_dir
    │   └── foo_file.py
    ├── hello_world.py
    └── README.md
    """
    dirs_to_walk = ["."]
    while dirs_to_walk:
        root = dirs_to_walk.pop(0)
        dirs, files = deepcopy(tree[root])
        yield root, dirs, files
        for d in dirs:
            dirs_to_walk.append(root + "/" + d)
