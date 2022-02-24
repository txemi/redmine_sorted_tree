import bisect

import attrs

from issue_wrapper import IssueWrapper

import logging


@attrs.frozen
class RedmineIssueSorter:
    _sorted_list: list[IssueWrapper] = attrs.field(factory=list)

    def add(self, issue_wrapped: IssueWrapper):
        if 2845 == issue_wrapped.get_id():
            logging.info("")
        show_in_report = issue_wrapped.is_shown_in_report()
        if not show_in_report:
            return
        bisect.insort(self._sorted_list, issue_wrapped)

    def get_items(self):
        return self._sorted_list
