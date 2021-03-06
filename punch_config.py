__config_version__ = 1

GLOBALS = {
    'serializer': "{{ MAJOR }}.{{ MINOR }}.{{ PATCH }}{{ '-{}'.format(PRERELEASE) if PRERELEASE }}"
}

FILES = ['setup.py',
         'dcspy/dcspy.py',
         'dcspy/starter.py']

VERSION = ['MAJOR',
           'MINOR',
           'PATCH',
           {'name': 'PRERELEASE',
            'type': 'value_list',
            'allowed_values': ['', 'alpha', 'beta']}]

# VCS = {
#     'name': 'git',
#     'commit_message': (
#         "Version updated from {{ current_version }}"
#         " to {{ new_version }}")
# }
