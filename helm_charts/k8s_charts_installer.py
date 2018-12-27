#python>=3.5

import subprocess
import os
import sys
import urwid
import shutil
from pathlib import Path


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


def deploy_helm_chart_chosen(button):
    print("asdasd")
    subprocess.call(["helm", "upgrade", "ingress-traefik", "--install", "stable/traefik", "--namespace", "ingress-traefik", "-f", "deployments/ingress-traefik/values.local.yml"])


def exit_program(button):
    raise urwid.ExitMainLoop()


menu_top = menu(u'Main Menus', [
    sub_menu(u'Install Helm Charts', [
        sub_menu(u'Accessories', [
            menu_button(u'Text Editor', item_chosen),
            menu_button(u'Terminal', deploy_helm_chart_chosen),
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


# Make sure python 3.5 and above is used
if sys.version_info[0] < 3 or sys.version_info[1] < 5:
    print("Python 3.5 is a minimal requirement")
    exit(1)

# Make sure config.local exists
config_file = Path(str(Path.home()) + "/.kube/config.local")
if not config_file.exists():
    print("Could not locate {}\nMake sure to create it".format(config_file))
    exit(1)

os.environ["KUBECONFIG"] = str(config_file)

# Make sure kubectl command exists
if shutil.which("kubectl") is None:
    print("Could execute 'kubectl' command\nMake sure 'kubectl' installed")
    exit(1)

# .run return CompletedProcess with returncode and stdout and stderr values as bytes object, using UTF-8 decode
cluster_info_output = subprocess.run(["kubectl", "cluster-info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# In case returncode is not 0
if cluster_info_output.returncode:
    print(cluster_info_output.stderr.decode('utf-8') +
          "Make sure your cluster is up and running, and config file contains correct values")
    exit(1)
else:
    print(cluster_info_output.stdout.decode('utf-8'))

top = CascadingBoxes(menu_top)
urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
