

# function for reading the csv file

def get_file_labels(file_path):
    import csv
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        labels = next(reader)
    return labels

# function to get the filename for the 

def get_filename(file_path):
    import os
    return os.path.basename(file_path)


# function to get similarity metric options for dropdown menu
# based on the fariba documentation

def get_similarity_metric_options():
    return ["EQUALITY", "EUCLIDEAN", "HAVERSINE", "JACCARD", "COSINE"]

def get_feature_type_options():
    return ["NOMINAL", "NUMERIC", "GEOGRAPHIC", "TIME", "DATE", "SET", "TEXT"]

def get_config_file_preview(config_path):
    with open(config_path, 'r') as file:
        content = file.read()
    return content