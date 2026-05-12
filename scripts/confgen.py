import os

def confgen(
    input_file_path, layer_name, primary_key_columns, feature_column,
    feature_type, similarity_metric, threshold,
    range_val="NULL", multi_range="NULL", num_segments="NULL",
    longitude_col="NULL", latitude_col="NULL",
    date_metric="NULL", date_format="NULL", time_format="NULL",
):
    input_file_name = os.path.basename(input_file_path)
    input_dir = os.path.dirname(os.path.abspath(input_file_path))

    # auto-detect the MLN_USR (datasets) directory from the path
    parts = input_dir.replace("\\", "/").split("/")
    if "datasets" in parts:
        mln_usr = "/".join(parts[:parts.index("datasets") + 1])
    else:
        mln_usr = input_dir

    input_dir_rel = os.path.relpath(input_dir, mln_usr).replace(os.sep, "/")
    # output goes to layers_generated sibling of data_files
    output_dir = os.path.join(os.path.dirname(input_dir), "layers_generated")
    output_dir_rel = os.path.relpath(output_dir, mln_usr).replace(os.sep, "/")

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(input_dir, f"{layer_name}.gen")

    with open(output_path, "w") as file:
        file.write(f"INPUT_DIRECTORY=$MLN_USR/{input_dir_rel}\n")
        file.write(f"OUTPUT_DIRECTORY=$MLN_USR/{output_dir_rel}\n")
        file.write("USERNAME=default\n\n")
        file.write("BEGIN_LAYER\n")
        file.write(f"INPUT_FILE_NAME= {input_file_name}\n")
        file.write(f"LAYER_NAME={layer_name}\n")
        file.write("LAYER_GENERATION_TYPE=System_Generated\n")
        file.write(f"PRIMARY_KEY_COLUMN={','.join(primary_key_columns)}\n")
        file.write(f"FEATURE_COLUMN={feature_column}\n")
        file.write(f"FEATURE_TYPE={feature_type}\n")
        file.write(f"SIMILARITY_METRIC={similarity_metric}\n")
        file.write(f"THRESHOLD={threshold if threshold and threshold != 'NULL' else 'NULL'}\n")
        file.write(f"RANGE={range_val}\n")
        file.write(f"MULTI_RANGE={multi_range}\n")
        file.write(f"NUMBER_OF_EQUI_SIZED_SEGMENTS={num_segments}\n")
        file.write(f"LONGITUDE_FEATURE_COLUMN={longitude_col}\n")
        file.write(f"LATITUDE_FEATURE_COLUMN={latitude_col}\n")
        file.write(f"DATE_METRIC={date_metric}\n")
        file.write(f"DATE_FORMAT={date_format}\n")
        file.write(f"TIME_FORMAT={time_format}\n")
        file.write("END_LAYER\n")
    return output_path
