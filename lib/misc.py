import os
import shutil

def copy_template(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        print(f'Creating {dst} from {src}; you might want to change it')
        shutil.copy(src, dst)
        return True
    else:
        return False
