
import urwid
from init_checks import init_checks
from helm_functions import *


def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')


def sub_menu(caption, choices):
    contents = menu(caption, choices)

    def open_menu(button):
        return top.open_box(contents)
    return menu_button([caption, u''], open_menu)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button):
    response = urwid.Text([u'You chose ', button.label, u'\n'])
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def terminate_chosen(button):
    response = urwid.Text([u'Application will now terminate!'])
    done = menu_button(u'Ok', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def exit_program(button):
    raise urwid.ExitMainLoop()


class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box):
        super(CascadingBoxes, self).__init__(urwid.SolidFill(u'/'))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(urwid.LineBox(box),
                                             self.original_widget,
                                             align='center', width=('relative', 80),
                                             valign='middle', height=('relative', 80),
                                             min_width=24, min_height=8,
                                             left=self.box_level * 3,
                                             right=(self.max_box_levels - self.box_level - 1) * 3,
                                             top=self.box_level * 2,
                                             bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            return super(CascadingBoxes, self).keypress(size, key)


menu_top = menu(u'Main Menus', [
    sub_menu(u'Install Helm Charts', [
        sub_menu(u'Accessories', [
            menu_button(u'Text Editor', item_chosen),
            menu_button(u'Terminal', install_helm_charts),
        ]),
        menu_button(u'Terminate Application', terminate_chosen),
    ]),
    sub_menu(u'Remove Helm Charts', [
        sub_menu(u'Preferences', [
            menu_button(u'Appearance', item_chosen),
        ]),
        menu_button(u'Terminate Application', terminate_chosen),
    ]),
    menu_button(u'Terminate Application', terminate_chosen),
])

top = CascadingBoxes(menu_top)


def main():
    print("Starting applications, please wait...")
    init_checks()
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()


if __name__ == "__main__":
    main()
