import os
import filecmp
import shutil
from . import misc

def path_is_parent(parent_path, child_path):
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def delete_files(files):
    for file in files:
        os.remove(file)

def get_all_files(dir):
    out=[]
    for current_dir, dirs, files in os.walk( dir ):
        if len(files) == 0: continue

        for file in files:
            out.append(os.path.join( os.path.relpath(current_dir, dir), file ))
    return out[::-1] # reverse

def filter_ext(all_files,ext_array,exclude = False):
    out=[]
    for file in all_files:
        cur = os.path.splitext( file )
        if cur[1] == '':
            cur = ('',os.path.basename(cur[0]))
        
        keep = True

        if exclude:
            for ext in ext_array:
                if cur[1].lower() == ext:
                    keep = False
                    break
        else:
            keep = False
            for ext in ext_array:
                if cur[1].lower() == ext:
                    keep = True
                    break
        
        if keep:
            out.append( file )
    return out

def copy_aux_files(all_files,exts,src,dst,count):
    files = filter_ext(all_files,exts,exclude=True)

    for e in files[:]:
        if os.path.basename(e) in [".umc.yaml","umc.yaml",".umc_override"]:
            # print("Not transferring", e)
            files.remove(e)
    
    for file in files:
        sf = os.path.abspath(os.path.join(src,file))
        df = os.path.abspath(os.path.join(dst,file))
        
        if os.path.exists(df):
            # compare files to prevent unnecessary copies
            if filecmp.cmp(sf, df, shallow=True):
                count[1] += 1
                continue
        
        print(end='\r')
        st = "Copying to " + os.path.basename(dst) + ": " + os.path.basename(sf)
        st = misc.fit_in_one_line(st)
        print(st,end='')

        shutil.copy2(sf,df)
        count[0] += 1

def copy_dirtree(src,dst):
    if not os.path.exists(dst):
        os.mkdir(dst)
    
    for current_dir, dirs, _files in os.walk( src ):
        full = os.path.relpath(current_dir,src)
        for dir in dirs:
            leaf = os.path.join(full,dir)
            mirror = os.path.join(dst,leaf)
            
            os.makedirs( mirror, exist_ok=True )