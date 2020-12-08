import os
import pathlib
import re
import string
import yaml
import tensorflow as tf


def tag_punct_remover(input_text):
    """Does the following to a string:
    - lower case
    - remove punctuations
    - remove HTML tags

    Parameters
    ----------
    input_text : str
        String of characters.

    Returns
    -------
    tf.tensor
        Processed string converted into a tensor.
    """
    lowercase_text = tf.strings.lower(input_text)
    strip_html_text = tf.\
        strings.regex_replace(lowercase_text,
                              '<[^>]+>', ' ')
    no_punct_text = tf.\
        strings.regex_replace(strip_html_text,
                              '[%s]' % re.escape(string.punctuation), ' ')

    no_sing_charac_text = tf.\
        strings.regex_replace(no_punct_text,
                              '\s+[a-zA-Z]\s+', ' ')

    sing_wspaced_text = tf.\
        strings.regex_replace(no_sing_charac_text,
                              '\s+', ' ')

    return sing_wspaced_text


def process_file(file_path):
    """Reads in a text file and processes the text within it.

    Parameters
    ----------
    file_path : str
        String of characters.

    Returns
    -------
    tf.tensor
        Processed string converted into a tensor.
    """
    with open(file_path, 'r') as file:
        curr_txt = file.read()
    edit_text = tag_punct_remover(curr_txt)

    return edit_text


def main():
    """Main programme to read in raw data files and process them.

    Data inputs and outputs are stated in `./configs/params.yaml`.
    """
    with open('./params.yaml', 'r') as curr_file:
        args = yaml.safe_load(curr_file)

    txt_files_list = pathlib.\
        Path(args['data_prep']['raw_data_path']).rglob('*.txt')
    txt_files_list = list(txt_files_list)

    for filename in txt_files_list:
        curr_edit_text = process_file(filename)
        out_filename = re.sub('/raw/', '/processed/', str(filename))
        os.makedirs(os.path.dirname(out_filename), exist_ok=True)
        tf.io.write_file(
            out_filename, curr_edit_text)


if __name__ == '__main__':
    main()
