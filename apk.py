import zipfile
import json
from tempfile import NamedTemporaryFile

from dex_parser import Dex


class APK:
    def __init__(self, apk_path: str):
        self.apk_path = apk_path

    def is_apk(self):
        apk_file = zipfile.ZipFile(self.apk_path, mode="r")
        if 'AndroidManifest.xml' in apk_file.namelist():
            return True
        return False

    def is_xapk(self):
        with zipfile.ZipFile(self.apk_path, mode="r") as apk_file:
            if 'manifest.json' in apk_file.namelist():
                manifest = json.load(apk_file.open('manifest.json'))
                if 'xapk_version' in manifest:
                    return True
            return False

    def _process_dex_file(self, dex_file):
        dex = Dex.from_file(dex_file)
        return [c.type_name for c in dex.class_defs]

    def list_classes(self):
        classes = []
        if self.is_apk():
            with zipfile.ZipFile(self.apk_path, mode="r") as apk_file:
                for file_path in apk_file.namelist():
                    if file_path.endswith('.dex'):
                        with NamedTemporaryFile() as dex:
                            dex.write(apk_file.read(file_path))
                            classes.extend(self._process_dex_file(dex.name))
        elif self.is_xapk():
            with zipfile.ZipFile(self.apk_path, mode="r") as apk_file:
                for file_path in apk_file.namelist():
                    if file_path.endswith('.apk'):
                        with NamedTemporaryFile() as apk:
                            apk.write(apk_file.read(file_path))
                            a = APK(apk.name)
                            classes.extend(a.list_classes())
        return sorted(list(set(classes)))

apk = APK('apks/am.videodownload.five.xapk')
classes = apk.list_classes()
print(classes)
