import os
import time
import shutil

FILE_TO_WATCH = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\save.sav"  # The save file to monitor changes.
BACKUP_DIRECTORY = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\Backups"  # Backup directory to backup save files.
BACKUP_GENERIC_NAME = r"\backup{0}.sav"  """ File format extension of the generic name should
                                             be equal with the extension of the save file.
                                             DO NOT ERASE OR EDIT {0} PART OF THE GENERIC NAME
                                             IF YOU DON'T KNOW WHAT YOU ARE DOING!!!"""

class changeListener(object):
    def __init__(self, filetw, backupdir, backup_generic):
        self.file = filetw
        self.backupdir = backupdir
        self.backup_generic = backup_generic
        self.cached_stamp = os.stat(self.file).st_mtime
        self.file_count = 0
        with os.scandir(self.backupdir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    self.file_count+=1  """ This piece of code assumes that you only have
                                            backups in your backup directory."""

    def check_process(self):
        return True

    def listen(self):
        time.sleep(30)
        if self.cached_stamp != os.stat(self.file).st_mtime:
            self.cached_stamp = os.stat(self.file).st_mtime
            self.file_count+=1
            filename = self.backupdir + self.backup_generic.format(self.file_count)
            shutil.copyfile(self.file, filename)
            print("Backup copied successfully.")


if __name__ == "__main__":
    listener = changeListener(FILE_TO_WATCH, BACKUP_DIRECTORY, BACKUP_GENERIC_NAME)
    print("Listener started successfully.")
    # time.sleep(5)
    while listener.check_process():
        listener.listen()
