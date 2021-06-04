signature_lists = {
        'os_command': [
            'eval',
            "sink_hqbpillvul_execFile",
            'sink_hqbpillvul_exec',
            'sink_hqbpillvul_execSync',
            'sink_hqbpillvul_spawn',
            'sink_hqbpillvul_spawnSync',
            'sink_hqbpillvul_db'
            ],
        'xss': [
            'sink_hqbpillvul_http_write',
            'sink_hqbpillvul_http_setHeader'
            ],
        'proto_pollution': [
            'merge', 'extend', 'clone', 'parse'
            ],
        'code_exec': [
            'Function',
            'eval',
            "sink_hqbpillvul_execFile",
            'sink_hqbpillvul_exec',
            'sink_hqbpillvul_execSync',
            'sink_hqbpillvul_eval'
            ],
        'sanitation': [
            'parseInt'
            ],
        'path_traversal': [
            'pipe',
            'sink_hqbpillvul_http_write',
            'sink_hqbpillvul_http_sendFile',
            ],
        'depd': [
            'sink_hqbpillvul_pp',
            'sink_hqbpillvul_code_execution',
            'sink_hqbpillvul_exec'
            ]

}

def get_all_sign_list():
    """
    return a list of all the signature functions
    """
    res = []
    for key in signature_lists:
        res += signature_lists[key]

    return res

