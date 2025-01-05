def crop_callback_data_string(callback_data_string: str) -> str:
    while len(callback_data_string.encode('utf-8')) > 61:
        callback_data_string = callback_data_string[:-1]
    return callback_data_string
