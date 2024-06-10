import fake_useragent


def generate_user_agents(num_agents):
    user_agents = []
    ua = fake_useragent.UserAgent()
    for _ in range(num_agents):
        user_agents.append(ua.random)
    return user_agents


def save_to_file(user_agents, filename):
    with open(filename, 'a') as f:
        for ua in user_agents:
            f.write(ua + '\n')


def main():
    num_agents = 100000  # Change this number to generate more or fewer user agents
    user_agents = generate_user_agents(num_agents)
    save_to_file(user_agents, 'user_agents.txt')


if __name__ == "__main__":
    main()
