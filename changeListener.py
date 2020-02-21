import os
import time
from datetime import datetime
import shutil
try:
    import psutil
    PSUTIL = True
except:
    PSUTIL = False
try:
    import gntp.notifier
    GNTP = True
except:
    GNTP = False

FILE_TO_WATCH = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\save.sav"  # The save file to monitor changes. Use FULL PATH.
BACKUP_DIRECTORY = r"C:\Users\YOUR-USER-NAME\Documents\My Games\SOME-GAME\saves\Backups"  # Backup directory to backup save files. Use FULL PATH.
PROCESS_IMAGE_NAME = "explorer.exe"  # The name of the process.
LEGACY = True  # You can flip this to False (actually, it is recommended) to try the new generic backup name.
               # New generic backup name? What? Surprise, surprise! It is based on time!
               # I mean, you already made me import datetime. Why not use it here as well?


class changeListener(object):
    def __init__(self, filetw, backupdir, process_im):
        self.file = filetw
        self.backupdir = backupdir
        self.process_im = process_im
        self.cached_stamp = os.stat(self.file).st_mtime
        if not os.path.exists(self.backupdir):
            os.makedirs(self.backupdir)
        if LEGACY:
            self.backup_generic = "backup{0}-" + self.find_filename(self.file)  # This is legacy.
            self.file_list = []  # This is legacy.
            self.file_count = 0  # This is also legacy.
            with os.scandir(self.backupdir) as it:
                # This code block will likely be removed in the next version.
                for entry in it:
                    if entry.name.startswith('backup') and entry.is_file():
                        self.file_list.append(entry.name)
                        self.file_count+=1
        if GNTP:
            self.notifier = gntp.notifier.GrowlNotifier(
                applicationName = "Change Listener",
                notifications = ["Message"],
                defaultNotifications = ["Message"])
            try:
                self.notifier.register()
            except gntp.errors.NetworkError:
                """If your Growl path is different than mine, you should change
                this string. Just don't touch the r at the start. That indicates
                the string should pass as raw string."""
                os.startfile(r"C:\Program Files (x86)\Growl for Windows\Growl.exe")
                self.notifier.register()

    def notify(self, message, stcky = False, prio = 0):
        message = "[{timestamp}] {message}".format(
            timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            message=message
        )
        if GNTP:
            self.notifier.notify(
                noteType = "Message",
                title = "Notification",
                description = message,
                sticky = stcky,
                priority = prio)
        else:
            print(message)

    def find_filename(self, file_path):
        try:
            return os.path.basename(file_path)
        except:
            self.notify("Faced an error while handling filename.", True, 2)
            # If you don't use full path, this error is going to issue.
            if GNTP:
                raise SystemExit
            else:
                input("Press Enter to exit.")
                raise SystemExit

    def check_process(self):
        if PSUTIL:
            return self.process_im in (p.name() for p in psutil.process_iter())
        else:
            return True

    def listen(self):
        time.sleep(10)  # For checking every 10 seconds.
        if self.cached_stamp != os.stat(self.file).st_mtime:
            while self.cached_stamp != os.stat(self.file).st_mtime:
                self.cached_stamp = os.stat(self.file).st_mtime
                time.sleep(15)
                """Some games (like Football Manager) don't write the save file as a whole,
                but write it part by part. This situation ends up with 5 or 6 backup files but
                just one of them meant to be. By adding this while loop with 15 seconds interval,
                I'm aiming to bypass the mentioned situation."""
            if LEGACY:
                self.file_count+=1
                filename = os.path.join(self.backupdir, self.backup_generic.format(self.file_count))
                while self.find_filename(filename) in self.file_list:
                    self.file_count+=1
                    filename = os.path.join(self.backupdir, self.backup_generic.format(self.file_count))
            else:
                filename = os.path.join(self.backupdir, "bkp-{time}-{name}".format(
                    time=datetime.now().strftime('%Y%m%d%H%M%S'),
                    name=self.find_filename(self.file)
                ))
            shutil.copyfile(self.file, filename)
            self.notify("Backup copied successfully. File path: {}".format(filename))


if __name__ == "__main__":
    listener = changeListener(FILE_TO_WATCH, BACKUP_DIRECTORY, PROCESS_IMAGE_NAME)
    listener.notify("Listener started successfully.")
    if not PSUTIL:
        listener.notify("psutil module not found. You should manually shut the script down, or it will run forever.")
    time.sleep(30)
    while listener.check_process():
        listener.listen()
    listener.notify("Listener closed due to termination of the main process.")
    if not GNTP:
       input("Press Enter to exit.")
