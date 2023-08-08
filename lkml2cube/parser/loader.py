import lkml

def file_loader(file_path):
    lookml_model = lkml.load(open(file_path, 'r'))
    return lookml_model
