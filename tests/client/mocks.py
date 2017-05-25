# -*- coding: utf-8 -*
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
    return [
       ['.', ['bar_dir', 'baz_dir', 'foo_dir'], ['hello_world.py', 'README.md']],
       ['./bar_dir', ['bar_dir_2'], ['bar_data.h5']],
       ['./bar_dir/bar_dir_2', ['bar_dir_3'], ['bar_file.py']],
       ['./bar_dir/bar_dir_3', [], ['bar_data.h5']],
       ['./baz_dir', ['baz_dir_2'], []],
       ['./baz_dir/baz_dir_2', ['baz_dir_3'], ('baz_file.md', 'baz_file.txt')],
       ['./foo_dir', [], ['foo_file.py']],
    ]
