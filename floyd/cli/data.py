import click
import sys
import os
import os.path
from tabulate import tabulate
import webbrowser

import floyd
from floyd.client.data import DataClient
from floyd.client.dataset import DatasetClient
from floyd.exceptions import FloydException
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.data_config import DataConfig, DataConfigManager
from floyd.log import logger as floyd_logger
from floyd.cli.data_upload_utils import (
    opt_to_resume, upload_is_resumable, abort_previous_upload,
    initialize_new_upload, complete_upload
)
from floyd.cli.utils import (
    normalize_data_name,
    get_namespace_from_name
)


@click.group()
def data():
    """
    Subcommand for data operations.
    """
    pass


@click.command()
@click.argument('dataset-name', nargs=1)
def init(dataset_name):
    """
    Initialize a new dataset at the current dir.

    Then run the upload command to copy all the files in this
    directory to FloydHub.

        floyd data upload
    """
    dataset_obj = DatasetClient().get_by_name(dataset_name)

    if not dataset_obj:
        namespace, name = get_namespace_from_name(dataset_name)
        create_dataset_base_url = "{}/datasets/create".format(floyd.floyd_web_host)
        create_dataset_url = "{}?name={}&namespace={}".format(create_dataset_base_url, name, namespace)
        floyd_logger.info(("Dataset name does not match your list of datasets. "
                           "Create your new dataset in the web dashboard:\n\t%s"),
                          create_dataset_base_url)
        webbrowser.open(create_dataset_url)

        name = click.prompt('Press ENTER to use dataset name "%s" or enter a different name' % dataset_name, default=dataset_name, show_default=False)

        dataset_name = name.strip() or dataset_name
        dataset_obj = DatasetClient().get_by_name(dataset_name)

        if not dataset_obj:
            raise FloydException('Dataset "%s" does not exist on floydhub.com. Ensure it exists before continuing.' % dataset_name)

    namespace, name = get_namespace_from_name(dataset_name)
    data_config = DataConfig(name=name,
                             namespace=namespace,
                             family_id=dataset_obj.id)
    DataConfigManager.set_config(data_config)
    floyd_logger.info("Data source \"{}\" initialized in current directory".format(dataset_name))
    floyd_logger.info("""
    You can now upload your data to Floyd by:
        floyd data upload
    """)


@click.command()
@click.option('-r', '--resume',
              is_flag=True, default=False, help='Resume previous upload')
@click.option('--message', '-m', default='',
              help='Job commit message')
def upload(resume, message):
    """
    Upload files in the current dir to FloydHub.
    """
    data_config = DataConfigManager.get_config()

    if not upload_is_resumable(data_config) or not opt_to_resume(resume):
        abort_previous_upload(data_config)
        access_token = AuthConfigManager.get_access_token()
        initialize_new_upload(data_config, access_token, message)

    complete_upload(data_config)


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    View status of all versions in a dataset.

    The command also accepts a specific dataset version.
    """
    if id:
        data_source = DataClient().get(normalize_data_name(id))

        if not data_source:
            # Try with the raw ID
            data_source = DataClient().get(id)

        print_data([data_source] if data_source else [])
    else:
        data_sources = DataClient().get_all()
        print_data(data_sources)


def print_data(data_sources):
    """
    Print dataset information in tabular form
    """
    if not data_sources:
        return

    headers = ["DATA NAME", "CREATED", "STATUS", "DISK USAGE"]
    data_list = []
    for data_source in data_sources:
        data_list.append([data_source.name,
                          data_source.created_pretty,
                          data_source.state, data_source.size])
    floyd_logger.info(tabulate(data_list, headers=headers))


@click.command()
@click.argument('id', nargs=1)
def clone(id):
    """
    Download all files in a dataset.
    """

    data_source = DataClient().get(normalize_data_name(id, use_data_config=False))
    if id and not data_source:
        # Try with the raw ID
        data_source = DataClient().get(id)

    if not data_source:
        if 'output' in id:
            floyd_logger.info("Note: You cannot clone the output of a running job. You need to wait for it to finish.")
        sys.exit()

    data_url = "{}/api/v1/resources/{}?content=true&download=true".format(floyd.floyd_host,
                                                                          data_source.resource_id)
    DataClient().download_tar(url=data_url,
                              untar=True,
                              delete_after_untar=True)


@click.command()
@click.argument('data_name', nargs=1)
def listfiles(data_name):
    """
    List files in a dataset.
    """

    data_source = DataClient().get(normalize_data_name(data_name, use_data_config=False))
    if data_name and not data_source:
        # Try with the raw ID
        data_source = DataClient().get(data_name)

    if not data_source:
        if 'output' in data_name:
            floyd_logger.info("Note: You cannot clone the output of a running job. You need to wait for it to finish.")
        sys.exit()

    # Depth-first search
    dirs = ['']
    paths = []
    while dirs:
        cur_dir = dirs.pop()
        url = "/resources/{}/{}?content=true".format(data_source.resource_id, cur_dir)
        response = DataClient().request("GET", url).json()

        if response['skipped_files'] > 0:
            floyd_logger.info("Warning: in directory '%s', %s/%s files skipped (too many files)", cur_dir, response['skipped_files'], response['total_files'])

        files = response['files']
        files.sort(key=lambda f: f['name'])
        for f in files:
            path = os.path.join(cur_dir, f['name'])
            if f['type'] == 'directory':
                path += os.sep
            paths.append(path)

            if f['type'] == 'directory':
                dirs.append(os.path.join(cur_dir, f['name']))
    for path in paths:
        floyd_logger.info(path)


@click.command()
@click.argument('data_name', nargs=1)
@click.argument('path', nargs=1)
def getfile(data_name, path):
    """
    Download a specific file from a dataset.
    """

    data_source = DataClient().get(normalize_data_name(data_name, use_data_config=False))
    if data_name and not data_source:
        # Try with the raw ID
        data_source = DataClient().get(data_name)

    if not data_source:
        if 'output' in data_name:
            floyd_logger.info("Note: You cannot clone the output of a running job. You need to wait for it to finish.")
        sys.exit()

    url = "{}/api/v1/resources/{}/{}?content=true".format(floyd.floyd_host, data_source.resource_id, path)
    fname = os.path.basename(path)
    DataClient().download(url, filename=fname)


@click.command()
@click.option('-u', '--url', is_flag=True, default=False,
              help='Only print url for viewing data')
@click.argument('id', nargs=1, required=False)
def output(id, url):
    """
    View the files from a dataset.
    """
    data_source = DataClient().get(normalize_data_name(id))
    if id and not data_source:
        # Try with the raw ID
        data_source = DataClient().get(id)

    if not data_source:
        sys.exit()

    data_url = "%s/%s" % (floyd.floyd_web_host, data_source.name)
    if url:
        floyd_logger.info(data_url)
    else:
        floyd_logger.info("Opening output directory in your browser ...")
        webbrowser.open(data_url)


@click.command()
@click.argument('ids', nargs=-1)
@click.option('-y', '--yes', is_flag=True, default=False,
              help='Skip confirmation')
def delete(ids, yes):
    """
    Delete datasets.
    """
    failures = False

    for id in ids:
        data_source = DataClient().get(normalize_data_name(id))
        if not data_source:
            # Try with the raw ID
            data_source = DataClient().get(id)

        if not data_source:
            failures = True
            continue

        data_name = normalize_data_name(data_source.name)
        suffix = data_name.split('/')[-1]
        if not suffix.isdigit():
            failures = True
            floyd_logger.error('%s is not a dataset, skipped.', id)
            if suffix == 'output':
                floyd_logger.error('To delete job output, please delete the job itself.')
            continue

        if not yes and not click.confirm("Delete Data: {}?".format(data_name),
                                         abort=False,
                                         default=False):
            floyd_logger.info("Data %s: Skipped", data_name)
            continue

        if not DataClient().delete(data_source.id):
            failures = True
        else:
            floyd_logger.info("Data %s: Deleted", data_name)

    if failures:
        sys.exit(1)


@click.command()
@click.argument('source')
def add(source):
    """
    Create a new dataset version from the contents of a job.

    This will create a new dataset version with the job output.
    Use the full job name: foo/projects/bar/1/home or foo/projects/bar/1/output
    """
    new_data = DatasetClient().add_data(source)
    print_data([DataClient().get(new_data['data_id'])])


data.add_command(clone)
data.add_command(delete)
data.add_command(init)
data.add_command(upload)
data.add_command(status)
data.add_command(output)
data.add_command(add)
data.add_command(listfiles)
data.add_command(getfile)
