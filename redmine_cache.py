import typing

import redminelib
import attrs
import typeguard

import assertpy


@typeguard.typechecked
@attrs.define
class RedmineCachingWrapper:
    """ Preparando que todas las consultas a redmine pasen por aquí para cachear y reducir las llamadas de red"""
    _redmine: redminelib.Redmine
    _detect_caching_oportunity_counter_1: int = 0
    _cache_issue: dict = attrs.field(factory=dict)
    _cache_custom_field: dict = attrs.field(factory=dict)

    def _get_projects(self):
        project_resource = self._redmine.project
        projects = project_resource.all()
        return projects

    def _get_project_by_name(self, project_name):
        return self._redmine.project.get(project_name)

    def _get_project(self, projec_name: str) -> redminelib.resources.Project:
        if True:
            project_iot = self._get_project_by_name(projec_name)
            return project_iot
        else:
            for project1 in self._get_projects():
                name = project1.name
                description = project1.description
                if projec_name.lower() not in name.lower():
                    continue
                return project1

    def get_custom_field(self, label_id: int) -> redminelib.resources.CustomField:
        if not label_id in self._cache_custom_field:
            self._cache_custom_field[label_id] = self._redmine.custom_field.get(label_id)
        return self._cache_custom_field[label_id]

    def get_issue(self, issue_id: int):
        if issue_id not in self._cache_issue:
            newparent = self._redmine.issue.get(issue_id)
            from issue_wrapper import IssueWrapper
            la = IssueWrapper(newparent, self)
            self._cache_issue[issue_id] = la
        return self._cache_issue[issue_id]

    def get_project_issues(self, projec_name) -> typing.Generator:
        assert self._detect_caching_oportunity_counter_1 == 0
        self._detect_caching_oportunity_counter_1 += 1
        selected_project = self._get_project(projec_name)

        from issue_wrapper import IssueWrapper
        include_closed = True
        if include_closed:
            iterator_ = self._redmine.issue.filter(project_id=selected_project.identifier, status_id='*')
        else:
            # funciona pero no incluye cerradas
            iterator_ = selected_project.issues
        for issue in iterator_:
            wrapper = IssueWrapper(issue, self)
            assertpy.assert_warn(self._cache_issue).does_not_contain_key(wrapper.get_id())
            # assert wrapper.get_id() not in self._cache_issue
            self._cache_issue[wrapper.get_id()] = wrapper
            yield wrapper

    def update_custom_field(self, issue, sorting_order_field_name_new: str, updating_index: int):
        from issue_wrapper import IssueWrapper
        assert isinstance(issue, IssueWrapper)
        mydict = issue.update_custom_fields(sorting_order_field_name_new, updating_index)
        update_result = self._redmine.issue.update(issue.get_id(), custom_fields=mydict)
        return update_result
