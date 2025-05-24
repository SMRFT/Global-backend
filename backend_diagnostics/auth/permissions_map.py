PAGE_MAPPING = {
    '/_b_a_c_k_e_n_d/Global/adminreg/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/create_employee/':'GL-P-EP', 
    '/_b_a_c_k_e_n_d/Global/data-entitlements/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/get_data_departments/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/get_data_designation/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/getprimaryandadditionalrole/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/set_employee_password/':'GL-P-EL',
    
    '/_b_a_c_k_e_n_d/Global/update_department/<str:department_code>/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/update_designation/<str:designation_code>/':'GL-P-EAD',

    '/adminreg/':'GL-P-EAD',
    '/create_employee/': 'GL-P-EP',
    '/set_employee_password/':'GL-P-EL',
    '/update_department/<str:department_code>/':'GL-P-EAD',
    '/update_designation/<str:designation_code>/':'GL-P-EAD',    
}

PAGE_ACTION_MAPPING = {
    'xxx': {
        'DELETE':'RWD',
    },
}

GEN_ACTION_MAPPING = {
    'POST': 'RW',
    'PUT': 'RW',
    'DELETE': 'RW',
    'GET': 'R',
}
