
import argparse
import urwid
import urwid.raw_display
import urwid.web_display
from pathlib import Path
from helm_charts.helm_functions import *
from helm_charts.init_checks import init_checks
from helm_charts.kubectl_functions import *
from helm_charts.helper import *
# from helm_functions import *
# from init_checks import init_checks
# from kubectl_functions import *
# from helper import *

config_file = str(Path.home()) + "/.kube/config"
cluster_context = "docker-for-desktop"


def main():
    urwid.web_display.set_preferences("Urwid Tour")
    # try to handle short web requests quickly
    if urwid.web_display.handle_short_request():
        return

    global config_file
    global cluster_context

    parser = argparse.ArgumentParser(description='Python Helm Charts Installer')
    parser.add_argument('--config-file', help='Path to kubernetes config file, '
                                              'Default is `{}`'.format(config_file), required=False)
    parser.add_argument('--use-context', help='Cluster context name to use, '
                                              'Default is `{}`'.format(cluster_context), required=False)
    parser.add_argument('--helm-init', action='store_true', help='Perform "helm init" on cluster', required=False)

    args = vars(parser.parse_args())

    if args['config_file'] is not None:
        config_file = args['config_file']

    if args['use_context'] is not None:
        cluster_context = args['use_context']

    print("Starting application, please wait...")
    init_checks(config_file, cluster_context, args['helm_init'])
    start_urwid()


def start_urwid():
    text_header = (u"Helm charts installer -  "
                   u"UP / DOWN / PAGE UP / PAGE DOWN scroll.  ctrl+e exits.")
    text_footer = remove_ansi_color_from_string(get_cluster_info().split("\n")[0])
    text_intro = [('important', u"Helm charts installer "),
                  u"installs kubernetes helm charts on a configured cluster, "
                  u"by default its intended to work on a cluster on the local host. "
                  u"\nFor more details execute 'helm_charts -h'"]
    config_context_info = [u"Current config file:   ", ('important', config_file),
                           u"\nCurrent context used:  ", ('important', cluster_context)]

    text_repos_divider = [u"Installed ", ('important', u"Helm repositories:")]

    helm_repo_installed_repositories_text = urwid.Text(identify_installed_helm_repos(return_only_decoded_string=True).replace("\t", "    "))
    helm_repo_installed_repositories_dict = identify_installed_helm_repos()

    helm_repo_name_edit_box = urwid.Edit(('editcp', u"Helm repo name "), "set name", align='left', )
    helm_repo_url_edit_box = urwid.Edit(('editcp', u"Helm repo URL  "), "set url", align='left', )
    helm_repo_add_result = urwid.Text('')

    helm_charts_installed_dict = identify_installed_helm_charts()

    text_charts_divider = [u"Installed ", ('important', u"Helm charts:")]
    text_helm_charts_installed = identify_installed_helm_charts(return_only_decoded_string=True).replace("\t", "    ")

    text_button_list = [u"Yes", u"No", u"Perhaps", u"Certainly", u"Partially", u"Tuesdays Only", u"Help"]

    text_rb_list = [u"Morning", u"Afternoon", u"Evening", u"Weekend"]

    def button_press(button):
        frame.footer = urwid.AttrWrap(urwid.Text(
            [u"Pressed: ", button.get_label()]), 'header')

    def add_repo_button_pressed(button):
        """
        Execute once 'Add repository' button pressed,
        function will init the 'add_helm_repo' function,
        update the 'text_helm_repo_installed_repositories' urwid.TEXT object
        and update 'helm_repo_add_result' urwid.TEXT object

        :param button:
        :return:
        """

        add_helm_repo_output = add_helm_repo(helm_repo_name_edit_box.edit_text,
                                             helm_repo_url_edit_box.edit_text)['value']
        [urwid.AttrWrap(urwid.CheckBox("{:30}{}".format(txt['repo_name'], txt['repo_url'])), 'buttn', 'buttnf')
         for txt in identify_installed_helm_repos()]
        helm_repo_installed_repositories_text.set_text(identify_installed_helm_repos(return_only_decoded_string=True).replace("\t", "    "))
        helm_repo_add_result.set_text(add_helm_repo_output)

    radio_button_group = []

    blank = urwid.Divider()
    listbox_content = [
        blank,
        urwid.Padding(urwid.Text(text_intro), left=2, right=2, min_width=20),
        blank,
        urwid.Padding(urwid.Text(config_context_info), left=2, right=2, min_width=20),

        urwid.WidgetWrap(urwid.Divider("=", 1)),
        urwid.Padding(urwid.Text(text_charts_divider), left=2, right=2, min_width=20),
        urwid.WidgetWrap(urwid.Divider("*", 0, 1)),

        # Display helm charts block ###########
        # urwid.Padding(
        #     urwid.Pile([
        #         urwid.Text("    {:30}{}".format("NAME", "NAMESPACE")),
        #         urwid.Pile(
        #             [urwid.AttrWrap(urwid.CheckBox("{:30}{}".format(chart['chart_name'], chart['name_space'])), 'buttn',
        #                             'buttnf') for chart in helm_charts_installed_dict],
        #         ),
        #
        #     ]), left=2, right=2, min_width=10),
        #######################################
        # Helm charts display
        urwid.Padding(urwid.Text(text_helm_charts_installed), left=2, right=2, min_width=20),

        urwid.WidgetWrap(urwid.Divider("=", 1)),
        urwid.Padding(urwid.Text(text_repos_divider), left=2, right=2, min_width=20),
        urwid.WidgetWrap(urwid.Divider("*", 0, 1)),

        # Display helm repositories block #####
        # urwid.Padding(
        #     urwid.Pile([
        #         urwid.Text("    {:30}{}".format("NAME", "URL")),
        #         urwid.Pile(
        #             [urwid.AttrWrap(urwid.CheckBox("{:30}{}".format(repo['repo_name'], repo['repo_url'])), 'buttn',
        #                             'buttnf') for repo in helm_repo_installed_repositories_dict],
        #         ),
        #
        #     ]), left=2, right=2, min_width=10),
        #######################################

        # Helm repositories display
        urwid.Padding(helm_repo_installed_repositories_text, left=2, right=2, min_width=20),
        blank,
        urwid.Padding(urwid.AttrWrap(helm_repo_name_edit_box, 'editbx', 'editfc'), left=2, right=2),
        urwid.Padding(urwid.AttrWrap(helm_repo_url_edit_box, 'editbx', 'editfc'), left=2, right=2),
        blank,
        urwid.Padding(urwid.AttrWrap(urwid.Button("Add repository", add_repo_button_pressed), 'buttn', 'buttnf'), left=2, right=2, width=18),
        blank,
        urwid.Padding(helm_repo_add_result, left=2, right=2, min_width=20),
        blank,

        # urwid.WidgetWrap(urwid.Columns([
        #     urwid.Divider("#"),
        #     urwid.Divider('$'),
        #     urwid.Divider("&"),
        #     urwid.Divider('"'),
        #     urwid.Divider("'"),
        #     ])),
        #
        # blank,
        # urwid.Padding(urwid.GridFlow(
        #     [urwid.AttrWrap(urwid.Button(txt, button_press), 'buttn','buttnf') for txt in text_button_list],
        #     13, 3, 1, 'left'),
        #     left=4, right=3, min_width=13),
        #
        # blank,
        # urwid.Padding(urwid.GridFlow(
        #     [urwid.AttrWrap(urwid.RadioButton(radio_button_group, txt), 'buttn','buttnf')
        #         for txt in text_rb_list],
        #     13, 3, 1, 'left') ,
        #     left=4, right=3, min_width=13),
        # blank,
        ]

    header = urwid.AttrWrap(urwid.Text(text_header), 'header')
    footer = urwid.AttrWrap(urwid.Text(text_footer), 'footer')
    listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

    # Frame widget is used to keep the instructions at the top of the screen
    frame = urwid.Frame(urwid.AttrWrap(listbox, 'body'), header=header, footer=footer)

    palette = [
        ('body', 'black', 'light gray', 'standout'),
        ('reverse', 'light gray', 'black'),
        ('header', 'white', 'dark red', 'bold'),
        ('footer', 'white', 'dark green', 'bold'),
        ('important', 'dark blue', 'light gray', ('standout', 'underline')),
        ('editfc', 'white', 'dark blue', 'bold'),
        ('editbx', 'light gray', 'dark blue'),
        ('editcp', 'black', 'light gray', 'standout'),
        ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
        ('buttn', 'black', 'light blue'),
        ('buttnf', 'white', 'dark blue', 'bold'),
        ]

    # use appropriate Screen class
    if urwid.web_display.is_web_request():
        screen = urwid.web_display.Screen()
    else:
        screen = urwid.raw_display.Screen()

    def unhandled(key):
        if key == 'ctrl e':
            raise urwid.ExitMainLoop()

    urwid.MainLoop(frame, palette, screen, unhandled_input=unhandled).run()


if __name__ == '__main__':
    main()
