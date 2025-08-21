PAGE_MAPPING = {
    '/_b_a_c_k_e_n_d/Global/adminreg/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/create_employee/':'GL-P-EP', 
    '/_b_a_c_k_e_n_d/Global/data-entitlements/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/get_data_departments/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/get_data_designation/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/getprimaryandadditionalrole/':'GL-P-EP',
    '/_b_a_c_k_e_n_d/Global/set_employee_password/':'GL-P-EL',
    '/_b_a_c_k_e_n_d/Global/set_employee_status/':'GL-P-P',
    '/_b_a_c_k_e_n_d/Global/get_employees_with_labels/':'GL-P-ED',
    '/_b_a_c_k_e_n_d/Global/update_department/.*/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/update_designation/.*/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/get_employee_by_id/.*/':'GL-P-ED',

    '/_b_a_c_k_e_n_d/Global/serve_file/': 'GL-P-ED',
    '^/_b_a_c_k_e_n_d/Global/update_employee/.*/': 'GL-P-ED',  # Regex for update_employee with any employee_id

    
    '/_b_a_c_k_e_n_d/Global/update_department/.*/':'GL-P-EAD',
    '/_b_a_c_k_e_n_d/Global/update_designation/.*/':'GL-P-EAD',


    '/adminreg/':'GL-P-EAD',
    '/create_mployee/': 'GL-P-EP',
    '/set_employee_password/':'GL-P-EL',

    '/update_department/.*/':'GL-P-EAD',
    '/update_designation/.*/':'GL-P-EAD',
    '/get_employees_with_labels/': 'GL-P-ED',
    '/get_data_departments/': 'GL-P-EP',
    '/get_data_designation/': 'GL-P-EP',
    '/getprimaryandadditionalrole/': 'GL-P-EP',
    '/get_employee_by_id/.*/': 'GL-P-ED',
    '/update_employee/.*/': 'GL-P-ED',
    '/serve_file/': 'GL-P-EL',


    '/update_department/<str:department_code>/':'GL-P-EAD',
    '/update_designation/<str:designation_code>/':'GL-P-EAD',

        

    '/update_department/.*/':'GL-P-EAD',
    '/update_designation/.*/':'GL-P-EAD',

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
    'DISPATCH': 'RW',  # ✅ Added dispatch mapping
}



