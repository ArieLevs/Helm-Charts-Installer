
import urwid
from subprocess import run, PIPE


class DeleteChartsMenu:

    def __init__(self, return_func, helm_charts_installed_dict):

        self.selection_ch_box = [urwid.CheckBox("{:30}{}".format(repo['chart_name'], repo['name_space']))
                                 for repo in helm_charts_installed_dict]

        self.text_deletion_result = urwid.Text(u"")

        blank = urwid.Divider()
        listbox_content = [
            blank,
            urwid.WidgetWrap(urwid.Divider("=", 1)),
            urwid.Padding(urwid.Text(u"Helm Charts Removal"), left=2, right=2, min_width=20),
            urwid.WidgetWrap(urwid.Divider("*", 0, 1)),
            urwid.Padding(urwid.Text(u"Use space/enter to mark helm chart to delete"), left=2, right=2, min_width=20),
            blank,

            # Display helm charts block
            urwid.Padding(
                urwid.Pile([
                    urwid.Text("    {:30}{}".format("NAME", "NAMESPACE")),
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
        charts_to_delete = []
        for chart in self.selection_ch_box:
            if chart.get_state():
                # split() without arguments splits on whitespace, get first cell of split
                charts_to_delete.append(chart.label.split()[0])
        # If the array remained empty
        if not charts_to_delete:
            self.text_deletion_result.set_text(u"At least one chart must be selected")
        else:
            result = delete_helm_installations(charts_to_delete)
            self.return_func(True)
        # self.text_installation_result.set_text(u'%s' % result)


def delete_helm_installations(charts_array):
    """
    Execute 'helm delete' command on input values
    charts_array is an array of strings as:
    ['ingress-traefik', 'kubernetes-dashboard', ...]

    :param charts_array: array of strings
    :return: return code and value from execution command as dict
    """
    status = 0
    value = 'no errors found'
    for installation in charts_array:
        completed_process_object = run(["helm", "delete", "--purge", installation], stdout=PIPE, stderr=PIPE)
        # In case of a non 0 return code, update return from last iteration
        if completed_process_object.returncode != 0:
            status = completed_process_object.returncode
            value = completed_process_object.stderr.decode('utf-8') + " *** Additional errors may occurred"
    return {'status': status, 'value': value}
