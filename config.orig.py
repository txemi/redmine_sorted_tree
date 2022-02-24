# edit me and rename to config.py

# Connection:
redmine_url = 'http://redmine.mycompany.com'
username = 'myuser'
password = 'mypass'

# Filtering:
project_name = 'project_name'
custom_labels_field_name = 'mylabels'

chapter_labels = ("level1chapter", "level2chapter")
# issues below this does not sort by sibling, sencodary criteria you specify in report instead

report_labels = ("show_in_report",) + chapter_labels
# issues that should appear in report


# sorting:
sibling_order_field_name = "SiblingOrder"
# sibling order you must update for issues this script will tell you

sorting_order_field_name_new = "report_sorting_index_new"
# this field will be updated by this script, you will use in redmine queries for sorting as first criteria.
