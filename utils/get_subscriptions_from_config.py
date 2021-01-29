import yaml

from pprint import pprint

def get_subscriptions_from_config(config: str) -> list:
    config_dict = {}
    with open(config, 'r') as stream:
        try:
            config_dict = yaml.safe_load(stream)
            config_dict = config_dict['exchanges']
            stream.close()
        except yaml.YAMLError as exc:
            print(f"Error reading from {config_dict}. {exc}")
    subscriptions = []
    for exchange, refdata in config_dict.items():
        if 'l2_book' in refdata:
            syms = refdata['l2_book']['symbols']
            for sym in syms:
                full_name = f"{exchange}-{sym}"
                if full_name not in subscriptions:
                    subscriptions.append(full_name)
    return subscriptions