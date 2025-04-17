PAGE_MAPPING = {
    '/admin_registration/':'GL-P-EAD',
    '/create_employee/': 'GL-P-EP',
    '/set_employee_password/':'GL-P-EL',
    '/update_department/':'GL-P-EAD',
    '/update_designation/':'GL-P-EAD',
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
