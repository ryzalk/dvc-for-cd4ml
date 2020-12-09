import os
import datetime
import pathlib
import yaml
import tensorflow as tf
import tensorflow_hub as hub
import wandb


def init_model(args):
    """Initialise model.

    Paramaters
    ----------
    args : dict
        A dictionary contained imported arguments from 'configs' folder.

    Returns
    -------
    tf.keras.Model
        Compiled sequential model.
    """

    hub_layer = hub.KerasLayer(
        args['train']['pretrained_embedding'], input_shape=[],
        dtype=tf.string, trainable=True)

    model = tf.keras.Sequential()
    model.add(hub_layer)
    model.add(tf.keras.layers.Dense(16, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

    model.compile(
        optimizer=args['train']['optimiser'],
        loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=[args['train']['metric']])

    return model

def load_datasets(args):
    """Load datasets specified through YAML config.

    Paramaters
    ----------
    args : dict
        A dictionary contained imported arguments from 'configs' folder.

    Returns
    -------
    dict
        Dictionary object for which its values are 'tf.data.Dataset' objects.
    """

    data_path = args['train']['data_path']

    train_ds = tf.keras.preprocessing.text_dataset_from_directory(
        os.path.join(data_path, 'train'),
        batch_size=args['train']['bs'],
        validation_split=args['train']['val_split'],
        subset='training',
        seed=args['train']['seed'])

    val_ds = tf.keras.preprocessing.text_dataset_from_directory(
        os.path.join(data_path, 'train'),
        batch_size=args['train']['bs'],
        validation_split=args['train']['val_split'],
        subset='validation',
        seed=args['train']['seed'])

    test_ds = tf.keras.preprocessing.text_dataset_from_directory(
        os.path.join(data_path, 'test'),
        batch_size=args['train']['bs'])

    datasets = {
        'train': train_ds,
        'val': val_ds,
        'test': test_ds
    }

    return datasets


def create_md_file(wnb_run_ent, wnb_run_proj,
                   wnb_run_id, model_eval_metrics):
    """This function creates a markdown file to be submitted as a GitHub comment.

    Paramaters
    ----------
    wnb_run_ent : str
        String containing W&B username.
    wnb_run_proj : str
        String containing W&B project run is to be parked under.
    wnb_run_proj : str
        String containing unique ID of the run.
    model_eval_metrics : tuple
        Tuple containing evaluation loss and accuracy of the model.
    """
    curr_dir = pathlib.Path().absolute()
    md_file_path = curr_dir / './train-run-metrics.md'
    md_file_path.write_text('# Model Metrics\n')
    file_obj = open(md_file_path, 'a')
    file_obj.write(r'__Link to run:__ https://wandb.ai/{}/{}/runs/{}'.\
                   format(wnb_run_ent, wnb_run_proj, wnb_run_id))
    file_obj.write('\n')
    file_obj.write(r'__Model Loss:__ {}'.\
                   format(model_eval_metrics[0]))
    file_obj.write('\n')
    file_obj.write(r'__Model Accuracy:__ {}'.\
                   format(model_eval_metrics[1]))
    file_obj.close()


def export_model(model):
    """Serialises and exports the trained model.

    Parameters
    ----------
    model : tf.keras.Model
        Trained model.
    """
    pathlib.Path('./models/').mkdir(parents=False, exist_ok=True)
    curr_path = pathlib.Path().absolute()
    model_file_path = curr_path / './models/text-classification-model'
    model.save(model_file_path)


def main():
    """This main function does the following:
    - load config parameters
    - initialise experiment tracking (Weights & Biases)
    - loads training, validation and test data
    - initialises model layers and compile
    - trains, evaluates, and then exports the model
    """
    with open('./params.yaml', 'r') as curr_file:
        args = yaml.safe_load(curr_file)

    now = datetime.datetime.now()
    dt_string = now.strftime('%d%m%y_%H%M%S')

    wandb.init(entity=args['train']['wnb_entity'],
               project=args['train']['wnb_project'],
               name=dt_string, config=args['train'])

    datasets = load_datasets(args)

    model = init_model(args)

    print('Training the model...')
    model.fit(
        datasets['train'],
        epochs=args['train']['epochs'],
        validation_data=datasets['val'],
        callbacks=[wandb.keras.WandbCallback()])

    print('Evaluating the model...')
    eval_metrics = model.evaluate(datasets['test'])

    create_md_file(wandb.run.entity, wandb.run.project,
                   wandb.run.id, eval_metrics)

    export_model(model)


if __name__ == '__main__':
    main()
