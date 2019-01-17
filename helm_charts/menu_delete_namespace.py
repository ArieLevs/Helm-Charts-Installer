
import urwid
from subprocess import run, PIPE


class DeleteNamespacesMenu:

    def __init__(self, return_func, available_namespaces_dict):

        self.available_namespaces_dict = available_namespaces_dict
        self.selection_ch_box = [urwid.CheckBox("{:30}{:30}{}".format(namespace['name'],
                                                                      namespace['status'],
                                                                      namespace['age']))
                                 for namespace in available_namespaces_dict]
        self.text_deletion_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Namespace Removal"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark Namespaces to remove"), left=2, right=2, min_width=20),
            blank,

            # Display namespaces block
            urwid.Padding(
                urwid.Pile([
                    urwid.Text("    {:30}{:30}{}".format("NAME", "STATUS", "AGE")),
                    urwid.Pile(
                        [urwid.AttrWrap(namespace, 'buttn', 'buttnf') for namespace in self.selection_ch_box],
                    ),

                ]), left=2, right=2, min_width=10),

            blank,
            urwid.Padding(
                urwid.GridFlow(
                    [urwid.AttrWrap(urwid.Button("Cancel", on_press=self.on_cancel), 'buttn', 'buttnf'),
                     blank,
                     urwid.AttrWrap(urwid.Button("Delete Selected Namespaces", on_press=self.on_delete), 'buttn', 'buttnf')
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
        namespaces_to_delete = []
        for index, namespace in enumerate(self.selection_ch_box):
            # If checkbox selected (True)
            if namespace.get_state():
                # Since selection_ch_box is built from available_namespaces_dict,
                # they share same values on same indexes
                namespaces_to_delete.append(self.available_namespaces_dict[index]['name'])

        # If the array remained empty
        if not namespaces_to_delete:
            self.text_deletion_result.set_text(u"At least one namespace must be selected")
        else:
            result = remove_namespaces(namespaces_to_delete)
            self.return_func(refresh_namespaces=True, returned_result=result)


def remove_namespaces(namespaces_array):

    """
    Execute 'kubectl repo remove' command on input values
    namespaces_array is an array of strings as:
    ['namespace1', 'anothername', 'nalkinscloud', ...]

    :param namespaces_array: array of strings
    :return: return code and value from execution command as dict
    """
    status = 0
    value = 'no errors found'

    command_array = ["kubectl", "delete", "namespaces"] + namespaces_array

    completed_process_object = run(command_array, stdout=PIPE, stderr=PIPE)
    # In case of a non 0 return code, update return from last iteration
    if completed_process_object.returncode != 0:
        status = completed_process_object.returncode
        value = completed_process_object.stderr.decode('utf-8')

    return {'status': status, 'value': value}
