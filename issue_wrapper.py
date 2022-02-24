import logging
import typing

import redminelib
import attrs
import config

import typeguard

from redmine_cache import RedmineCachingWrapper


@attrs.frozen
class AncestorCalculator:
    _issue: "IssueWrapper"

    def parents(self):
        return self._issue.parents()


@typeguard.typechecked
@attrs.frozen
class IssueWrapper:
    # TODO: split class: generic basic issue logic + report sorting specific logic
    _issue: redminelib.resources.Issue
    _redmine: RedmineCachingWrapper

    def get_custom_field_by_name(self, name):
        for custom_field in self._issue.custom_fields:
            if custom_field.name == name:
                return custom_field

    def first_common_ancestor(self, i2):
        assert isinstance(self, IssueWrapper)
        assert isinstance(i2, IssueWrapper)
        a1 = AncestorCalculator(self)
        a2 = AncestorCalculator(i2)
        for step in self.parents():
            for step2 in i2.parents():
                if step.match(step2):
                    return step

    def get_custom_field_values(self, name):
        # id = 28 aa = self._issue.custom_fields.get(28)
        iot_labels = self.get_custom_field_by_name(name)
        if iot_labels is None:
            return
        iot_labels_value = iot_labels.value
        if iot_labels_value == '':
            return

        custom_field_def = self._redmine.get_custom_field(iot_labels.id)
        for found_possible_value in iot_labels_value:
            found_possible_value_int = int(found_possible_value)
            for possible_value in custom_field_def.possible_values:
                if possible_value['value'] == found_possible_value:
                    yield possible_value['label']

    def _get_labels(self):
        # id = 28 aa = self._issue.custom_fields.get(28)
        return list(self.get_custom_field_values(config.custom_labels_field_name))

    def _iot_labels_match(self, lala):
        for iot_label in self._get_labels():
            if iot_label in lala:
                return True
        return False

    def is_shown_in_report(self):
        return self._iot_labels_match(config.report_labels)

    def _just_below(self, stop):
        if self.get_wrapped_parent().get_id() == stop.get_id():
            return self
        return self.get_wrapped_parent()._just_below(stop)

    def _is_chapter(self):
        return self._iot_labels_match(config.chapter_labels)

    def _get_ancestor_chapter_block_issue(self):
        ascending = self
        while True:
            if ascending._is_chapter():
                return ascending
            ascending = ascending.get_wrapped_parent()
            if ascending is None:
                break

    def _below_chapter_ancestor_issue(self):
        return self._get_ancestor_chapter_block_issue() is not None

    def _contains(self, other):
        assert isinstance(other, IssueWrapper)
        corredor = other
        while True:
            if corredor.get_id() == self.get_id():
                return True
            corredor = corredor.get_wrapped_parent()
            if corredor is None:
                break
        return False

    def get_sibling_order(self) -> typing.Optional[int]:
        custom_field = self.get_custom_field_by_name(config.sibling_order_field_name)
        if custom_field is None:
            return
        value = custom_field.value
        if value == "":
            return
        try:
            return int(value)
        except:
            raise

    def _compare_lt_using_sibling(self, other) -> bool:
        assert isinstance(other, IssueWrapper)
        if self._contains(other):
            return True
        if other._contains(self):
            return False
        f_c_a = self.first_common_ancestor(other)
        if False:
            if f_c_a._below_chapter_ancestor_issue():
                return False
        sort_candidate_1 = self._just_below(f_c_a)
        sort_candidate_2 = other._just_below(f_c_a)
        order1 = sort_candidate_1.get_sibling_order()
        order2 = sort_candidate_2.get_sibling_order()
        if order1 is None and order2 is None:
            return False
        result = order1 < order2

        return result

    def same_chapter_block(self, other):
        assert isinstance(other, IssueWrapper)
        # ambos tendrían que ser hoja no?
        if self._is_chapter():
            return False
        if other._is_chapter():
            return False
        i1block = self._get_ancestor_chapter_block_issue()
        if i1block is None:
            return False
        i2block = other._get_ancestor_chapter_block_issue()
        if i2block is None:
            return False
        try:
            return i1block.match(i2block)
        except:
            raise

    def _are_sorting_index_equal(self, other) -> bool:
        same_block = self.same_chapter_block(other)
        if same_block:
            return True
        return False

    def __lt__(self, other):
        assert isinstance(other, IssueWrapper)
        if 2570 in (self.get_id(), other.get_id()):
            logging.info("")
        result_parent_sibling = self._compare_lt_using_sibling(other)

        return result_parent_sibling

    def get_wrapped_parent(self):
        try:
            parent = self._issue.parent
        except redminelib.exceptions.ResourceAttrError:
            # si no tiene padre pues no pasa nada
            return
        newparent_wrapper = self._redmine.get_issue(parent.id)
        return newparent_wrapper

    def parents(self):
        newparent_wrapper = self.get_wrapped_parent()
        if newparent_wrapper is None:
            return
        assert newparent_wrapper is not None
        yield newparent_wrapper
        for next_ancestor in newparent_wrapper.parents():
            yield next_ancestor

    def get_id(self) -> int:
        aa = self._issue.id
        return aa

    def match(self, other) -> bool:
        try:
            return self.get_id() == other.get_id()
        except:
            raise

    def update_custom_fields(self, name: str, value):
        selected_custom_field = self.get_custom_field_by_name(name)
        selected_custom_field.value = str(value)

        custom_field_list = []
        for other_custom_field2 in self._issue.custom_fields:
            if other_custom_field2.id == selected_custom_field.id:
                custom_field_list.append({'id': selected_custom_field.id, 'value': selected_custom_field.value})
            else:
                try:
                    value = other_custom_field2.value
                except:
                    logging.exception("exception catched")
                else:
                    try:
                        custom_field_list.append({'id': other_custom_field2.id, 'value': value})
                    except:
                        raise
        return custom_field_list
