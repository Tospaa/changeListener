import os
import time
import shutil

FILE_TO_WATCH = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\save.sav"  # The save file to monitor changes.
BACKUP_DIRECTORY = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\Backups"  # Backup directory to backup save files.


def find_ext(file_path):
    indx = -1
    for _ in range(len(file_path)):
        if file_path[indx] == ".":
            return file_path[indx:]
        indx-=1
    return ""

def find_filename(file_path):
    indx = -1
    for _ in range(len(file_path)):
        if file_path[indx] == "\\":
            return file_path[indx+1:]
        indx-=1
    raise ValueError("Internal error. That shouldn't have happened.")

class changeListener(object):
    def __init__(self, filetw, backupdir):
        self.file = filetw
        self.backupdir = backupdir
        self.backup_generic = r"\backup{0}" + find_ext(self.file)
        self.cached_stamp = os.stat(self.file).st_mtime
        self.file_list = []
        self.file_count = 0
        if not os.path.exists(self.backupdir):
            os.makedirs(self.backupdir)
        with os.scandir(self.backupdir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    self.file_list.append(entry.name)
                    self.file_count+=1

    def check_process(self):
        return True

    def listen(self):
        time.sleep(30)
        if self.cached_stamp != os.stat(self.file).st_mtime:
            self.cached_stamp = os.stat(self.file).st_mtime
            self.file_count+=1
            filename = self.backupdir + self.backup_generic.format(self.file_count)
            while find_filename(filename) in self.file_list:
                self.file_count+=1
                filename = self.backupdir + self.backup_generic.format(self.file_count)
            shutil.copyfile(self.file, filename)
            print("Backup copied successfully.")


if __name__ == "__main__":
    listener = changeListener(FILE_TO_WATCH, BACKUP_DIRECTORY)
    print("Listener started successfully.")
    # time.sleep(5)
    while listener.check_process():
        listener.listen()
