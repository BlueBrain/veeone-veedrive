import argparse
import asyncio
import os
import random
import time
from argparse import RawTextHelpFormatter
from multiprocessing import Manager, Pool

import scandir

import veedrive.config
import veedrive.content.content_manager
from veedrive.content import utils
from veedrive.content.content_manager import cache_thumbnail

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument(
    "--source",
    "-s",
    dest="source",
    type=str,
    help="Path to media content",
    default="/nfs4/bbp.epfl.ch/media/DisplayWall",
)
parser.add_argument(
    "--destination",
    "-d",
    dest="destination",
    type=str,
    help="Path to cache content",
    default="/tmp",
)
parser.add_argument(
    "--cpu",
    "-c",
    dest="no_cpu",
    type=int,
    help="Number of cpu to use",
    default=os.cpu_count(),
)

parser.add_argument(
    "--report",
    "-r",
    dest="report",
    type=int,
    help="""Report detail level:
    O - print summary
    1 - print list of errors
    2 - print list of successful and skipped""",
    default=0,
)


args = parser.parse_args()


def print_report(result_dict, t_start):
    nb_ok = len(result_dict["ok"])
    nb_err = len(result_dict["err"])
    nb_skipped = len(result_dict["skipped"])

    if args.report == 2:
        if nb_skipped > 0:
            print("SKIPPED:")
            print(*(e + "\n" for e in (result_dict["skipped"])))
        if nb_err > 0:
            print("ERRORED:")
            print(*(e + "\n" for e in (result_dict["err"])))
        if nb_ok:
            print("OK:")
            print(*(e + "\n" for e in (result_dict["ok"])))
    if args.report == 1:
        if nb_err > 0:
            print("ERRORED:")
            print(*(e + "\n" for e in (result_dict["err"])))
    print(f"[INFO] Success: {nb_ok}, Errors: {nb_err}, Skipped: {nb_skipped}")
    print(f"[INFO] Elapsed time is {time.perf_counter() - t_start:.2} seconds")


def get_all_supported_files(sandbox_root):
    def is_supported(file_name):
        return (
            os.path.splitext(file_name)[1].lower()
            in veedrive.config.SUPPORTED_THUMBNAIL_EXTENSIONS
        )

    scan_result = scandir.walk(sandbox_root)

    all_files = []
    for path, directories, files in scan_result:
        if files:
            rel_path = os.path.relpath(path, sandbox_root)
            if rel_path == ".":
                rel_path = ""
            all_files += [
                os.path.join(rel_path, f) for f in files if is_supported(e)
            ]
    return all_files


def chunk(list_to_chunk, chunk_size):
    for i in range(0, len(list_to_chunk), chunk_size):
        yield list_to_chunk[i : i + chunk_size]


def generate_thumbnails(images_to_convert, media_path, cache_folder, result_queue):
    veedrive.config.SANDBOX_PATH = media_path

    for f in images_to_convert:
        try:
            cache_thumbnail(f, cache_folder)
            dic = result_queue.get()
            dic["ok"].append(f)
            result_queue.put(dic)
        except FileExistsError:
            dic = result_queue.get()
            dic["skipped"].append(f)
            result_queue.put(dic)
        except Exception as e:
            dic = result_queue.get()
            dic["err"].append(f)
            result_queue.put(dic)


async def main():
    media_path = args.source
    cache_folder = args.destination
    no_cpu = args.no_cpu
    chunk_size = 1

    if no_cpu > os.cpu_count():
        print("[WARN] Starting with cpu count bigger than actual cpu count")
    files = get_all_supported_files(media_path)
    random.shuffle(files)

    print(f"[INFO] No of files to generate: {len(files)}")
    number_of_files = len(files)

    if number_of_files < no_cpu:
        no_cpu = number_of_files

    print(f"[INFO] chunk size is {chunk_size}")
    chunked_list = list(chunk(files, chunk_size))

    print(f"[INFO] number of chunks is {len(chunked_list)}")

    utils.create_cache_subfolders(cache_folder)

    pool = Pool(processes=no_cpu)

    t_start = time.perf_counter()

    m = Manager()
    result_queue = m.Queue()
    result_queue.put({"ok": [], "err": [], "skipped": []})

    pool.starmap(
        generate_thumbnails,
        [(x, media_path, cache_folder, result_queue) for x in chunked_list],
        chunksize=1,
    )
    pool.terminate()
    result_dict = result_queue.get()

    print_report(result_dict, t_start)


if __name__ == "__main__":
    asyncio.run(main())
