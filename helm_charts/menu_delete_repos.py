
import urwid
from subprocess import run, PIPE


class DeleteReposMenu:

    def __init__(self, return_func, helm_repos_installed_dict):

        self.helm_repos_installed_dict = helm_repos_installed_dict
        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(repo['repo_name'], repo['repo_url']))
                                 for repo in helm_repos_installed_dict]
        self.text_deletion_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Helm Repositories Removal"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark helm repo to remove"), left=2, right=2, min_width=20),
            blank,

            # Display helm repositories block
            urwid.Padding(
                urwid.Pile([
                    urwid.Text("    {:30}{}".format("NAME", "URL")),
                    urwid.Pile(
                        [urwid.AttrWrap(chart, 'buttn', 'buttnf') for chart in self.selection_ch_box],
                    ),

                ]), left=2, right=2, min_width=10),

            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Delete Selected Charts", on_press=self.on_delete), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),
            blank,
            urwid.Padding(self.text_deletion_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func
        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_delete(self, w):
        repos_to_delete = []
        for index, chart in enumerate(self.selection_ch_box):
            # If checkbox selected (True)
            if chart.get_state():
                # Since selection_ch_box is built from helm_repos_installed_dict,
                # they share same values on same indexes
                repos_to_delete.append(self.helm_repos_installed_dict[index]['repo_name'])

        # If the array remained empty
        if not repos_to_delete:
            self.text_deletion_result.set_text(u"At least one repo must be selected")
        else:
            result = remove_helm_repo(repos_to_delete)
            self.return_func(refresh_installed_repos=True, returned_result=result)


def remove_helm_repo(repos_array):
    """
    Execute 'helm repo remove' command on input values
    repos_array is an array of strings as:
    ['stable', 'local', 'nalkinscloud', ...]

    :param repos_array: array of strings
    :return: return code and value from execution command as dict
    """
    status = 0
    value = 'no errors found'
    for repo in repos_array:
        completed_process_object = run(["helm", "repo", "remove", repo], stdout=PIPE, stderr=PIPE)
        # In case of a non 0 return code, update return from last iteration
        if completed_process_object.returncode != 0:
            status = completed_process_object.returncode
            value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"

    return {'status': status, 'value': value}
