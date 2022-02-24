import attrs

from issue_wrapper import IssueWrapper


@attrs.frozen
class Group:
    _issues: list[IssueWrapper] = attrs.field(factory=list)

    def match_and_add(self, new_issue: IssueWrapper):
        if len(self._issues) == 0:
            self._issues.append(new_issue)
            return True
        first = self._issues[0]
        if first.same_chapter_block(new_issue):
            self._issues.append(new_issue)
            return True
        return False

    def get_size(self):
        return len(self._issues)

    def get_issues(self):
        return self._issues


@attrs.frozen
class Groups:
    _groups: list[Group] = attrs.field(factory=list)
    pass

    def add(self, item: IssueWrapper):
        if len(self._groups) == 0:
            group = Group()
            group.match_and_add(item)
            self._groups.append(group)
            return

        last_group = self._groups[-1]
        if last_group.match_and_add(item):
            pass
        else:
            group = Group()
            group.match_and_add(item)
            self._groups.append(group)

    def get_groups(self):
        return self._groups