def read_credentials(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        credentials = {}
        for line in lines:
            key, value = line.strip().split(": ")
            credentials[key] = value
    return credentials
