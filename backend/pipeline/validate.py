import os


SUPPORTED_EXTENSIONS = {".csv", ".txt", ".tsv", ".seg"}


def validate_dataset_path(dataset_path):
    return os.path.isdir(dataset_path)


def validate_file_path(file_path):
    if not os.path.isfile(file_path):
        return False
    _, ext = os.path.splitext(file_path.lower())
    return ext in SUPPORTED_EXTENSIONS

