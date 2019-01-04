
import urwid
from subprocess import run, PIPE


class AddRepoMenu:

    def __init__(self, return_func):

        self.helm_repo_name_edit_box = urwid.Edit(('editcp', u"Helm repo name "), "set name", align='left', )
        self.helm_repo_url_edit_box = urwid.Edit(('editcp', u"Helm repo URL  "), "set url", align='left', )
        self.add_repo_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Add Helm Repository"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            blank,

            blank,
            urwid.Padding(urwid.AttrWrap(self.helm_repo_name_edit_box, 'editbx', 'editfc'), left=2, right=2),
            urwid.Padding(urwid.AttrWrap(self.helm_repo_url_edit_box, 'editbx', 'editfc'), left=2, right=2),
            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Add repository", on_press=self.on_add_repo), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),

            blank,
            urwid.Padding(self.add_repo_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func
        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_add_repo(self, w):
        """
        Execute once 'Add repository' button pressed,
        init the 'add_helm_repo' function,
        update the 'text_helm_repo_installed_repositories' urwid.TEXT object
        and update 'helm_repo_change_result' urwid.TEXT object

        :return:
        """

        # Execute the 'add repo' function with relevant values, and get the 'value' return from function
        add_helm_repo_output = add_helm_repo(self.helm_repo_name_edit_box.edit_text,
                                             self.helm_repo_url_edit_box.edit_text)
        if add_helm_repo_output['status'] != 0:
            self.add_repo_result.set_text(add_helm_repo_output['value'])
        else:
            return self.return_func(refresh_installed_repos=True, returned_result=add_helm_repo_output['value'])


def add_helm_repo(repo_name, repo_url):
    """
    Execute 'helm repo add' command on input values

    :param repo_name: name of repository as strings
    :param repo_url: url of repository as string
    :return: return code and value from execution command as dict
    """
    # execute and get CompletedProcess object
    completed_process_object = run(["helm", "repo", "add", repo_name, repo_url], stdout=PIPE, stderr=PIPE)
    if completed_process_object.returncode == 0:
        value = completed_process_object.stdout.decode('utf-8')
    else:
        value = completed_process_object.stderr.decode('utf-8')
    return {'status': completed_process_object.returncode, 'value': value}
