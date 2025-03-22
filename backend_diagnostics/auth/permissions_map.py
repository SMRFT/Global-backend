
PAGE_MAPPING = {
    '/create_employee/': 'GL-P-AB',
    '/barcode': 'SD-P-BAR',
    '/test': 'SD-P-TST',
    '/dummy': 'SD-P-DMY',
    # All page mappings...
}

PAGE_ACTION_MAPPING = {
    'SD-P-BAR': {
        'POST':'GBC',
    },
    'SD-P-BAR': {
        'PUT':'RBC',
    },
}

GEN_ACTION_MAPPING = {
    'POST': 'RW',
    'PUT': 'RW',
    'DELETE': 'RW',
    'GET': 'R',
}
