import os


def create_env_varaible(name, value):
    os.environ[name] = value


def create_file(f, file_content):
    with open(f, "w") as fil:
        fil.write(file_content)


def delete_files(f_lst):
    for f in f_lst:
        os.remove(f)


def delete_file_content(f):
    open(f, "w").close()
