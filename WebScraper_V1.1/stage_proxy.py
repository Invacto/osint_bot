def stage_proxy(file_path):
    def read_proxy_file(file_path):
        with open(file_path, 'r') as file:
            line = file.readline().strip()
            proxy_host, proxy_port, proxy_username, proxy_password = line.split(':')
        return proxy_host, proxy_port, proxy_username, proxy_password

    proxy_host, proxy_port, proxy_username, proxy_password = read_proxy_file(file_path)

    proxy_options = {
        'proxy': {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'https': f'https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    return proxy_options