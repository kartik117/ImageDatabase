"""Utility functions to display popup messages and file dialogs, and various functions related to Qt."""
import os
import pathlib
import platform
import subprocess
import typing as typ

import PyQt5.QtGui as QtG
import PyQt5.QtWidgets as QtW

from .. import constants, config
from ..i18n import translate as _t


def show_info(message: str, title='popup.info.title', parent: QtW.QWidget = None):
    """Shows an information popup.

    :param message: Popup’s message.
    :param title: Popup’s unlocalized title.
    :param parent: Popup’s parent.
    """
    mb = QtW.QMessageBox(QtW.QMessageBox.Information, _t(title), message, buttons=QtW.QMessageBox.Ok, parent=parent)
    mb.button(QtW.QMessageBox.Ok).setText(_t('dialog.common.ok_button.label'))
    mb.exec_()


def show_warning(message: str, title: str = 'popup.warning.title', parent: QtW.QWidget = None):
    """Shows a warning popup.

    :param message: Popup’s message.
    :param title: Popup’s unlocalized title.
    :param parent: Popup’s parent.
    """
    mb = QtW.QMessageBox(QtW.QMessageBox.Warning, _t(title), message, buttons=QtW.QMessageBox.Ok, parent=parent)
    mb.button(QtW.QMessageBox.Ok).setText(_t('dialog.common.ok_button.label'))
    mb.exec_()


def show_error(message: str, title: str = 'popup.error.title', parent: QtW.QWidget = None):
    """Shows an error popup.

    :param message: Popup’s message.
    :param title: Popup’s unlocalized title.
    :param parent: Popup’s parent.
    """
    mb = QtW.QMessageBox(QtW.QMessageBox.Critical, _t(title), message, buttons=QtW.QMessageBox.Ok, parent=parent)
    mb.button(QtW.QMessageBox.Ok).setText(_t('dialog.common.ok_button.label'))
    mb.exec_()


def show_question(message: str, title: str = 'popup.question.title', cancel: bool = False,
                  parent: QtW.QWidget = None) -> typ.Optional[bool]:
    """Shows a question popup.

    :param message: Popup’s message.
    :param title: Popup’s unlocalized title.
    :param cancel: If true a "Cancel" button will be added.
    :param parent: Popup’s parent.
    :return: True for yes, False for no or None for cancel.
    """
    answers = {
        QtW.QMessageBox.Yes: True,
        QtW.QMessageBox.No: False,
        QtW.QMessageBox.Cancel: None,
    }
    buttons = QtW.QMessageBox.Yes | QtW.QMessageBox.No
    if cancel:
        buttons |= QtW.QMessageBox.Cancel

    mb = QtW.QMessageBox(QtW.QMessageBox.Question, _t(title), message, buttons=buttons, parent=parent)
    mb.button(QtW.QMessageBox.Yes).setText(_t('dialog.common.yes_button.label'))
    mb.button(QtW.QMessageBox.No).setText(_t('dialog.common.no_button.label'))
    if cancel:
        mb.button(QtW.QMessageBox.Cancel).setText(_t('dialog.common.cancel_button.label'))
    # noinspection PyTypeChecker
    return answers[mb.exec_()]


def show_text_input(message: str, title: str, text: str = '', parent: QtW.QWidget = None) -> typ.Optional[str]:
    """Shows an input popup.

    :param message: Popup’s message.
    :param title: Popup’s title.
    :param text: Text to show in the input field.
    :param parent: Popup’s parent.
    :return: The typed text or None if the popup was cancelled.
    """
    input_d = QtW.QInputDialog(parent=parent)
    input_d.setWindowTitle(title)
    input_d.setLabelText(message)
    input_d.setTextValue(text)
    input_d.setOkButtonText(_t('dialog.common.ok_button.label'))
    input_d.setCancelButtonText(_t('dialog.common.cancel_button.label'))
    ok = input_d.exec_()
    return input_d.textValue() if ok else None


def show_int_input(message: str, title: str, value: int = 0, min_value: int = None, max_value: int = None,
                   parent: QtW.QWidget = None) -> typ.Optional[int]:
    """Shows an input popup.

    :param message: Popup’s message.
    :param title: Popup’s title.
    :param value: Value to show in the input field.
    :param min_value: Minimum value.
    :param max_value: Maximum value.
    :param parent: Popup’s parent.
    :return: The typed text or None if the popup was cancelled.
    """
    input_d = QtW.QInputDialog(parent=parent)
    input_d.setWindowTitle(title)
    input_d.setLabelText(message)
    input_d.setInputMode(QtW.QInputDialog.IntInput)
    if min_value is not None:
        input_d.setIntMinimum(min_value)
    if max_value is not None:
        input_d.setIntMaximum(max_value)
    input_d.setIntValue(value)
    input_d.setOkButtonText(_t('dialog.common.ok_button.label'))
    input_d.setCancelButtonText(_t('dialog.common.cancel_button.label'))
    ok = input_d.exec_()
    return input_d.intValue() if ok else None


FILTER_IMAGES = 0
FILTER_DB = 1


def open_file_chooser(single_selection: bool, mode: int, parent: QtW.QWidget = None) \
        -> typ.Union[typ.List[pathlib.Path], pathlib.Path, None]:
    """Opens a file chooser for images.

    :param single_selection: Whether the user can select only a single file.
    :param mode: What file filter to apply.
    :param parent: Chooser’s parent.
    :return: The selected files or None if the chooser was cancelled.
    """
    kwargs = {}
    if config.CONFIG.debug:
        kwargs['options'] = QtW.QFileDialog.DontUseNativeDialog
    if mode == FILTER_IMAGES:
        caption_k = 'image' if single_selection else 'images'
        filter_k = 'images'
        exts = ' '.join(map(lambda e: '*.' + e, constants.IMAGE_FILE_EXTENSIONS))
    else:
        caption_k = filter_k = 'database'
        exts = '*.sqlite3'
    function = QtW.QFileDialog.getOpenFileName if single_selection else QtW.QFileDialog.getOpenFileNames
    selection, _ = function(
        caption=_t('popup.file_chooser.caption.' + caption_k),
        filter=_t('popup.file_chooser.filter.' + filter_k) + f' ({exts})',
        parent=parent,
        **kwargs
    )

    if selection:
        def check_ext(p: str) -> bool:
            ext = os.path.splitext(p)[1].lower()[1:]
            return ((mode == FILTER_IMAGES and ext in constants.IMAGE_FILE_EXTENSIONS)
                    or (mode == FILTER_DB and ext == 'sqlite3'))

        # Check extensions if user removed filter
        if single_selection:
            return pathlib.Path(selection).absolute() if check_ext(selection) else None
        else:
            return [pathlib.Path(s).absolute() for s in selection if check_ext(s)]
    return None


def open_playlist_saver(parent: typ.Optional[QtW.QWidget] = None) -> typ.Optional[pathlib.Path]:
    """Opens a file saver for playlists.

    :param parent: Saver’s parent.
    :return: The selected file’s path or None if the saver was cancelled.
    """
    kwargs = {}
    if config.CONFIG.debug:
        kwargs['options'] = QtW.QFileDialog.DontUseNativeDialog
    ext = '.play'
    file, _ = QtW.QFileDialog.getSaveFileName(
        caption=_t('popup.playlist_saver.caption'),
        filter=_t('popup.playlist_saver.filter') + f' (*{ext})',
        parent=parent,
        **kwargs
    )
    if file and not file.endswith(ext):
        file += ext
    return pathlib.Path(file).absolute() if file else None


def open_directory_chooser(parent: QtW.QWidget = None) -> typ.Optional[typ.List[pathlib.Path]]:
    """Opens a directory chooser then returns all the image files it contains.

    :param parent: Chooser’s parent.
    :return: All image file paths directly inside the chosen directory or None if the chooser was cancelled.
    """
    options = QtW.QFileDialog.ShowDirsOnly
    if config.CONFIG.debug:
        options |= QtW.QFileDialog.DontUseNativeDialog
    directory = QtW.QFileDialog.getExistingDirectory(
        caption=_t('popup.open_directory_chooser.caption'),
        parent=parent,
        options=options
    )
    if directory:
        return [pathlib.Path(f).absolute() for f in pathlib.Path(directory).glob('*.*')
                if os.path.splitext(f.name)[1].lower()[1:] in constants.IMAGE_FILE_EXTENSIONS]
    return None


def choose_directory(parent: QtW.QWidget = None) -> typ.Optional[pathlib.Path]:
    """Opens a directory chooser.

    :param parent: Chooser’s parent.
    :return: The selected directory or None if the chooser was cancelled.
    """
    options = QtW.QFileDialog.ShowDirsOnly
    if config.CONFIG.debug:
        options |= QtW.QFileDialog.DontUseNativeDialog
    directory = QtW.QFileDialog.getExistingDirectory(
        caption=_t('popup.directory_chooser.caption'),
        parent=parent,
        options=options
    )
    return pathlib.Path(directory).absolute() if directory else None


def center(window: QtW.QWidget):
    """Centers the given window on the screen.

    :param window: The window to center.
    """
    rect = window.frameGeometry()
    center = QtW.QDesktopWidget().availableGeometry().center()
    rect.moveCenter(center)
    window.move(rect.topLeft())


def show_file(file_path: pathlib.Path):
    """Shows the given file in the system’s file explorer."""
    try:
        path = str(file_path.absolute())
    except RuntimeError:  # Raised if loop is encountered in path
        return
    os_name = platform.system().lower()
    if os_name == 'windows':
        subprocess.Popen(f'explorer /select,"{path}"')
    elif os_name == 'linux':
        command = ['dbus-send', '--dest=org.freedesktop.FileManager1', '--type=method_call',
                   '/org/freedesktop/FileManager1', 'org.freedesktop.FileManager1.ShowItems',
                   f'array:string:{path}', 'string:""']
        subprocess.Popen(command)
    elif os_name == 'darwin':  # OS-X
        subprocess.Popen(['open', path])


def negate(color: QtG.QColor) -> QtG.QColor:
    """Negates the given color.

    :param color: The base color.
    :return: The negated color.
    """
    return QtG.QColor(255 - color.red(), 255 - color.green(), 255 - color.blue())


_BLACK = QtG.QColor(0, 0, 0)
_WHITE = QtG.QColor(255, 255, 255)


def font_color(bg_color: QtG.QColor) -> QtG.QColor:
    """Computes the font color that will yeild the best contrast with the given background color.

    @see
    https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color

    :param bg_color: Background color.
    :return: Font color with highest contrast.
    """
    luminance = 0.2126 * bg_color.redF() + 0.7152 * bg_color.greenF() + 0.0722 * bg_color.blueF()
    return _BLACK if luminance > 0.179 else _WHITE


def icon(icon_name: str) -> QtG.QIcon:
    """Returns a QIcon for the given icon name.

    :param icon_name: Icon name, without file extension.
    :return: The QIcon object.
    """

    return QtG.QIcon(str(constants.ICONS_DIR / (icon_name + '.png')))


def get_key_sequence(event: QtG.QKeyEvent) -> QtG.QKeySequence:
    """Returns a QKeySequence object for the keystroke of the given event."""
    # noinspection PyTypeChecker
    return QtG.QKeySequence(event.modifiers() | event.key())


def event_matches_action(event: QtG.QKeyEvent, action: QtW.QAction) -> bool:
    """Checks whether the keystroke of the given event exactly matches any of the shortcuts of the given action."""
    ks = get_key_sequence(event)
    return any([s.matches(ks) == QtG.QKeySequence.ExactMatch for s in action.shortcuts()])
