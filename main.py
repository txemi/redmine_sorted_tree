import logging

from redminelib import Redmine

from chapter_issue_groups import Groups
from issue_wrapper import IssueWrapper
from redmine_issue_sorter import RedmineIssueSorter
import config
from redmine_cache import RedmineCachingWrapper
import typeguard


@typeguard.typechecked
def update_indexes_in_redmine(redmine: RedmineCachingWrapper, groups: Groups):
    updating_index = 100
    for group in groups.get_groups():
        for issue in group.get_issues():
            redmine.update_custom_field(issue, config.sorting_order_field_name_new, updating_index)
        updating_index += 10


@typeguard.typechecked
def redmine_issue_sort_and_update_index_in_redmine(redmine_sorter: RedmineIssueSorter, redmine: RedmineCachingWrapper):
    groups = Groups()
    for item in redmine_sorter.get_items():
        groups.add(item)
    for group in groups.get_groups():
        print(group.get_size())
    update_indexes_in_redmine(redmine, groups)


@typeguard.typechecked
def build_redmine_connection() -> RedmineCachingWrapper:
    redmine = Redmine(config.redmine_url,
                      username=config.username, password=config.password)
    redmine_orm = RedmineCachingWrapper(redmine)
    return redmine_orm


def recalc_indexes():
    redmine_orm = build_redmine_connection()

    redmine_sorter = RedmineIssueSorter()

    for wrapped_issue in redmine_orm.get_project_issues(config.project_name):
        assert isinstance(wrapped_issue, IssueWrapper)
        issue_id = wrapped_issue.get_id()
        if issue_id == 2845:
            logging.warning("")
        if wrapped_issue.is_shown_in_report():
            redmine_sorter.add(wrapped_issue)
    redmine_issue_sort_and_update_index_in_redmine(redmine_sorter, redmine_orm)


if __name__ == '__main__':
    recalc_indexes()
