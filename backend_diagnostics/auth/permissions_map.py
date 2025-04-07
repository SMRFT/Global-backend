PAGE_MAPPING = {
    '/create_employee/': 'GL-P-EPM',
}

PAGE_ACTION_MAPPING = {
    'GL-P-EPM': {
        'DELETE':'RWD',
    },
}

GEN_ACTION_MAPPING = {
    'POST': 'RW',
    'PUT': 'RW',
    'DELETE': 'RW',
    'GET': 'R',
}
