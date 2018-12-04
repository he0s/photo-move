#!/usr/bin/env python
# coding: utf-8

import argparse
import exifread
import logging
import os
import shutil
import sys
import traceback

from multiprocessing import Pool, cpu_count

COUNT = 5


class Photo:
    """
    The class describes basic model and methods of a media file.
    """
    def __init__(self, path, dest, mode):
        self.file = path[0]
        self.path = path[1]
        self.dest = dest
        self.mode = mode

    def get_exif(self):
        """
        The function to get EXIF information from a media file.
        """
        fl = open(self.path, 'rb')
        self.tags = exifread.process_file(fl)
        fl.close()

        try:
            if 'Image DateTime' in self.tags.keys():
                logging.debug('{}: {} --> {}'.format(
                    self.path,
                    'Image DateTime',
                    self.tags['Image DateTime']
                ))
                self.data = self.tags['Image DateTime']
            else:
                logging.warn('{}: {}'.format(
                    self.file,
                    "No 'Image DateTime' tag in EXIF info "
                ))
                self.data = False
        except Exception as e:
            logging.error('{}'.format(self.path))
            logging.error('Error: {}'.format(e))
            logging.error(traceback.print_exc(e))

    def mv_file(self):
        """
        The function what moves or makes a copy of a media file from
        source to destination.
        """

        def _operate_file(self):
            if self.mode != 'dry-run':
                if not os.path.exists(os.path.join(self.dest, self.file)):
                    if self.mode == 'copy':
                        logging.info(
                            'Copying of the file {}'.format(self.path)
                        )
                        shutil.copy(
                            self.path,
                            os.path.join(self.dest, self.file)
                        )
                    elif self.mode == 'move':
                        logging.info(
                            'Moving of the file {}'.format(self.path)
                        )
                        shutil.move(
                            self.path,
                            os.path.join(self.dest, self.file)
                        )
                elif os.path.exists(os.path.join(self.dest, self.file)):
                    logging.warn(
                        'The target file {} exists. Nothing to do'.format(
                            self.path
                        )
                    )

            else:
                if not os.path.exists(os.path.join(self.dest, self.file)):
                    logging.info(
                        'Moving of the file {}'.format(self.path)
                    )
                elif os.path.exists(os.path.join(self.dest, self.file)):
                    logging.warn(
                        'The target file {} exists. Nothing to do'.format(
                            self.path
                        )
                    )

        def _mv_file(self):
            if not os.path.isdir(self.dest):
                logging.info('Directory {} is not exists'.format(self.dest))
                logging.info('Creating the directory {}'.format(self.dest))

                if self.mode != 'dry-run':
                    try:
                        os.makedirs(self.dest)
                        _operate_file(self)
                    except Exception as e:
                        if e.errno == 17 and e.strerror == 'File exists':
                            _operate_file(self)
                        else:
                            logging.error('Error: {}'.format(e))
                            logging.error(traceback.print_exc(e))
                else:
                    logging.info(
                        'Moving of the file {}'.format(self.path)
                    )
            else:
                _operate_file(self)

        self.get_exif()

        if self.data:
            dir_name = str(self.data).split()[0]
            self.dest = os.path.join(self.dest, ''.join(dir_name.split(':')))
            _mv_file(self)

        else:
            self.dest = os.path.join(self.dest, '000_untagged')
            _mv_file(self)


def file_list(path):
    """
    The function to make list of files, located in the source path.
    :param str path: the path where the media files are located
    """
    if os.path.isdir(path):
        data = [(i, os.path.join(path, i)) for i in os.listdir(path)]
        if data:
            return data
        else:
            logging.info(
                'The {} directory is empty.'.format(path)
            )
            sys.exit(0)

    else:
        print('{} is not a directory'.format(path))
        sys.exit(0)


def operate(file_obj):
    file_obj.mv_file()


def move_func(args):
    """
    The function to move media files from source to destination.
    :param str args.source: the source of the media files
    :param str args.destination: the destination of the media files
    """

    if os.path.exists(args.source):
        data = file_list(args.source)

        if data:
            data = [Photo(i, args.destination, 'move') for i in data]

            pool = Pool(cpu_count()*COUNT)
            pool.map(operate, data)
            pool.close()
            pool.join()


def dry_func(args):
    """
    The function what does nothing except printing of information messages.
    :param str args.source: the source of the media files
    :param str args.destination: the destination of the media files
    """

    if os.path.exists(args.source):
        data = file_list(args.source)

        if data:
            data = [Photo(i, args.destination, 'dry-run') for i in data]

            pool = Pool(cpu_count()*COUNT)
            pool.map(operate, data)
            pool.close()
            pool.join()


def copy_func(args):
    """
    The function to copy media files from source to destination.
    :param str args.source: the source of the media files
    :param str args.destination: the destination of the media files
    """

    if os.path.exists(args.source):
        data = file_list(args.source)

        if data:
            data = [Photo(i, args.destination, 'copy') for i in data]

            pool = Pool(cpu_count()*COUNT)
            pool.map(operate, data)
            pool.close()
            pool.join()


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] --%(levelname)s-- %(message)s",
    )

    parser = argparse.ArgumentParser(
        description='The tool to sort and copy \
            photos from one directory to another.'
    )

    subparsers = parser.add_subparsers(help='The list of main commands.')

    move = subparsers.add_parser(
        'move',
        help="Move media file(s) from a source to a destination."
    )
    move.add_argument(
        '-s', '--source',
        action='store',
        help="Source path with media files."
    )
    move.add_argument(
        '-d', '--destination',
        action='store',
        help="Destination path, where media files will be moved."
    )
    move.set_defaults(func=move_func)

    dry_run = subparsers.add_parser(
        'dry-run',
        help="Dry-run mode. Does nothing, just prints information."
    )
    dry_run.add_argument(
        '-s', '--source',
        action='store',
        help="Source path with media files."
    )
    dry_run.add_argument(
        '-d', '--destination',
        action='store',
        help="Destination path, where media files will be moved."
    )
    dry_run.set_defaults(func=dry_func)

    copy = subparsers.add_parser(
        'copy',
        help="Copy media file(s) from a source to a destination."
    )
    copy.add_argument(
        '-s', '--source',
        action='store',
        help="Source path with media files."
    )
    copy.add_argument(
        '-d', '--destination',
        action='store',
        help="Destination path, where media files will be copied."
    )
    copy.set_defaults(func=copy_func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":

    main()
