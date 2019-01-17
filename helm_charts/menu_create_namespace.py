
import urwid
from subprocess import run, PIPE


class CreateNamespaceMenu:

    def __init__(self, return_func):

        self.create_namespace_edit_box = urwid.Edit(('editcp', u"Namespace to add: "), "set name", align='left', )
        self.create_namespace_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Create Namespace"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            blank,

            blank,
            urwid.Padding(urwid.AttrWrap(self.create_namespace_edit_box, 'editbx', 'editfc'), left=2, right=2),
            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Create", on_press=self.on_create_namespace), 'buttn', 'buttnf')
                     ],
                    20, 1, 8, 'left'),
                left=2, right=2, min_width=20, align='left'),

            blank,
            urwid.Padding(self.create_namespace_result, left=2, right=2, min_width=20),
        ]

        listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))

        self.return_func = return_func
        self.main_window = urwid.LineBox(urwid.AttrWrap(listbox, 'body'))

    def on_cancel(self, w):
        self.return_func()

    def on_create_namespace(self, w):
        """
        Execute once 'Create' button pressed,
        init the 'create_namespace' function,
        and update 'create_namespace_result' urwid.TEXT object

        :return:
        """

        # Execute the 'create_namespace' function with relevant values, and get the 'value' return from function
        create_namespace_output = create_namespace(self.create_namespace_edit_box.edit_text)
        if create_namespace_output['status'] != 0:
            self.create_namespace_result.set_text(("errors", create_namespace_output['value']))
        else:
            return self.return_func(refresh_namespaces=True, returned_result=create_namespace_output['value'])


def create_namespace(namespace_name):
    """
    Execute 'kubectl create namespace' command on input values

    :param namespace_name: name of namespace as string
    :return: return code and value from execution command as dict
    """
    # execute and get CompletedProcess object
    completed_process_object = run(["kubectl", "create", "namespace", namespace_name], stdout=PIPE, stderr=PIPE)
    if completed_process_object.returncode == 0:
        value = completed_process_object.stdout.decode('utf-8')
    else:
        value = completed_process_object.stderr.decode('utf-8')
    return {'status': completed_process_object.returncode, 'value': value}
