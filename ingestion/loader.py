def load_cert_dataset(paths: dict):
    data = {}

    for name, path in paths.items():
        data[name] = load_csv(path)

    return data