import os
import subprocess
import pathlib


def markup(filename):
    return '<file alias="{filename}">{filename}</file>'.format(
        filename=filename)


FILE_HEAD = """<!DOCTYPE RCC>
<RCC version="1.0">
<qresource>"""
FILE_TAIL = """
</qresource>
</RCC>"""
SPACING = "\n" + "    "
IMAGE_PATH = pathlib.Path.cwd().parent / "images"

image_filenames = list(os.walk(str(IMAGE_PATH)))[0][2]
file_body = SPACING + SPACING.join(
    markup(filename) for filename in image_filenames)
resource_file = FILE_HEAD + file_body + FILE_TAIL
with open(str(IMAGE_PATH / "resources.qrc"), "w") as resources:
    resources.write(resource_file)
subprocess.run("pyside2-rcc resources.qrc -o resources.py".split(" "),
               cwd=str(IMAGE_PATH))
