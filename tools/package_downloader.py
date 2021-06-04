import csv
import subprocess
import json
import argparse
import string
import os
import logging
from tqdm import tqdm

fail_log = logging.getLogger('fail_logger')
fail_handler = logging.FileHandler(filename="fail.log")
fail_log.addHandler(fail_handler)

success_log = logging.getLogger('success_logger')
success_handler = logging.FileHandler(filename="success.log")
success_log.addHandler(success_handler)


def download_package(name, version, target_path="./"):
    try:
        print("downloading {}@{}".format(name, version))
        if version is None:
            version = get_latest_version(name)
        dir_name = "{}@{}".format(name, version)
        target_package_path = os.path.abspath(os.path.join(target_path, dir_name))

        archive = "{}-{}.tgz".format(name, version)
        curl_cmd = 'curl --silent --remote-name https://registry.npmjs.org/{}/-/{}'.format(
            name, archive)

        os.system(curl_cmd)
        os.system('mkdir -p {}'.format(target_package_path))

        if archive[0] == '@':
            archive = archive.split('/')[1]
        os.system('tar xzf {} --strip-components 1 -C {}'.format(
            archive, target_package_path))
        os.system('rm {}'.format(archive))

    except:
        fail_log.info('{}@{} failed \n'.format(name, version))
        return

    success_log.info('{}@{} success \n'.format(name, version))

def handle_json_download(raw_filename, cut_all=None, cut_cur=None):
    """
    generate csv by raw file
    """
    package_list = []
    print(raw_filename)
    with open(raw_filename, 'r') as rf:
        os.system('mkdir -p packages')
        os.chdir("packages")
        name_list = json.load(rf)
        for line in name_list:
            package_name = line
            package_list.append(line)

        # split the packages
        block_size = int(len(package_list) / cut_all)
        start_id = cut_cur * block_size
        if cut_cur == cut_all:
            end_id = len(package_list)
        else:
            end_id = (cut_cur + 1) * block_size
        package_list = package_list[start_id : end_id]
        for package_name in package_list:
            version_number = get_latest_version(package_name)
            try:
                download_package(package_name, version_number)
                success_log.error("{},{}".format(package_name, version_number))
            except Exception as e:
                fail_log.error("{},{}".format(package_name, version_number))
                print(e)

def handle_csv_downlaod(filename):
    with open(filename, 'r') as fp:
        os.system('mkdir -p packages')
        os.chdir("packages")
        reader = csv.reader(fp, dialect='excel')
        tqdm_bar = tqdm(list(reader))
        for row in tqdm_bar:
            tqdm_bar.set_description("Installing {}".format(row[0].strip()))
            try:
                package_name = row[0].strip()
                package_name = package_name.lower()
                package_version = row[1].strip()
            except:
                fail_log.info('failed to parse npm package')
            download_package(package_name, package_version)

def main():
    parser = argparse.ArgumentParser(
        description='Process some integers.')
    parser.add_argument('-f', help='csv file')
    parser.add_argument('-r', help='raw file')
    parser.add_argument('-c', help='cut into n parts')
    parser.add_argument('-i', help='this thread is the ith part')
    args = parser.parse_args()
    filename = args.f  # "./test.csv"
    raw_filename = args.r

    if raw_filename:
        if args.c is not None:
            handle_json_download(raw_filename, cut_all=int(args.c), cut_cur=int(args.i))
    else:
        handle_csv_downlaod(filename)

def get_latest_version(name):
    command = "npm show {} version".format(name)
    out = subprocess.Popen(['npm', 'show', name, 'version'],
           stdout=subprocess.PIPE,
           stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    return stdout.decode('UTF-8').strip()

if __name__ == "__main__":
    main()


