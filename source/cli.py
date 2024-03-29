import argparse
import os
from pathlib import Path
import time

from . import conf, confwiz, fget, target

def wav2flac(files):
    for file in files:
        target.convert_file(file, os.path.splitext(file)[0] + ".flac")
    fget.delete_all(files)

def check_for_wavs_silent(all_files):
    files = fget.filter_ext(all_files,[".wav"])
    wav2flac(files)

def check_for_wavs(cwd,all_files):
    p_cwd = Path(cwd)
    files = [p_cwd.joinpath(f) for f in fget.filter_ext(all_files,[".wav",".WAV"])]
    
    if len(files) < 1: return
    
    print(files)
    conv_prompt = input("WAV file(s) detected. Would you like to convert them to FLAC to save space? ")

    if conv_prompt.lower()[0] != "y":
        return

    for i, f in enumerate(all_files):
        if Path(f).suffix.lower == ".wav" and not Path(f).with_suffix(".flac").exists():
            all_files[i] = str(Path(all_files[i]).with_suffix(".flac"))
    
    # temporary encode queue 
    enc_queue = [target.Encode(file,file.with_suffix(".flac"),opts="-map_metadata 0") for file in files if not Path(file).with_suffix(".flac").exists()]
    
    print(enc_queue)
    # print(Path(files[0]).with_suffix(".flac"))
    # print(Path(files[0]).with_suffix(".flac").exists())
    
    

    conv = target.ConverterParallel(target={"max_parallel_encodes": 3},enc_queue=enc_queue)
    conv.run()

    del_prompt = input("Would you like to *DELETE* the leftover WAV file(s)?")
    if del_prompt.lower()[0] == "y":
        fget.delete_files(files)
    
    del files
    del enc_queue

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="umc [OPTION] [CONFIG]"
    )
    parser.add_argument("-v","--version",action="version",
        version=f"{parser.prog} v0.1")
    parser.add_argument("-w","--wizard",action='store_true',
        help="shows configuration wizard")
    parser.add_argument("-q","--quiet",action='store_true',
        help="makes program less chatty")
    parser.add_argument('config_file',nargs="?")
    return parser


def converter(cwd, args, skip_wizard = False):
    cwd = os.path.expanduser(cwd)
    config = conf.init_config(cwd)

    print("Discovering files...")
    all_files = fget.get_all_files(cwd)
    
    print(str(len(all_files)) + " file(s)")
    

    if config == None or args.wizard:
        if skip_wizard:
            print("No config")
            return None
        config = confwiz.wizard(cwd)

    if config == None: return None

    if args.quiet:
        config["quiet"] = True

    if "wav2flac" in config:
        if config["wav2flac"]:
            check_for_wavs(cwd,all_files)
            all_files = fget.get_all_files(cwd)
    
    print(all_files[0])

    c_start = time.time()
    cli_out = target.process_targets(Path(cwd), all_files, config)
    c_end = time.time()

    print("Time elapsed: " + str(round(c_end-c_start)) + " seconds")
    return cli_out

def transcoder_server():
    pass

def main():
    parser = init_argparse()
    args = parser.parse_args()
    
    cwd = os.getcwd()
    if args.config_file:
        cwd = os.path.abspath(args.config_file)
        if os.path.isfile(cwd):
            cwd = os.path.split(cwd)[0]
    
    converter(cwd,args)