import yaml


if __name__ == "__main__":
    data = {
        'list': ['a', 'b', 'c'],
        'number': 42,
        'dict': {
            'key1': 100,
            'key2': 200,
            'key3': '€'
        }
    }

    with open('file.yaml', 'w', encoding='utf8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    with open('file.yaml', 'r', encoding='utf8') as f:
        loaded_data = yaml.load(f, Loader=yaml.FullLoader)

    print(data == loaded_data)
