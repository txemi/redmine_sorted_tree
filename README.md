# redmine_sorted_tree

Source: https://github.com/txemi/redmine_sorted_tree

## Motivation

In redmine you cannot sort by secondary criteria when sorting by parent in order to view issues hierarchically:
https://www.redmine.org/issues/10048

This is undesirable as you cannot make human readable queries on issues having issues sorted with your criteria as well as sorting to show hierarchy.

Example: One tipical report would be some treeview for high level issues like chapters in a book, sorting each level with in some way you define (sibling order) and finally you could want to sort bottom issues by due date, priority or version on each "chapter".

With this software you can achieve this.

## How does it work

This script will use custom fields on issues to achieve its objective via redmine REST API.
- Input: you can define some field as sibling order for children of same parent. I.e: sort issues like chapters of a book. You can also use "labels" coded in another custom field to filter issues that sould be sorted.
- Output: this code will fill in a numeric custom field your define to achieve this and you should use this field in queries in orther to get the sorted tree. Issues with no sibling order below same ancestor could be sorted with aditional fields as they are assigned same index.


## Quick Start

1. Download this code
2. Copy config.orig.py to config.py
3. Edit config.py with your preferences
4. Run main.py
5. Make query on redmine sorting by index you selected in config.py first, and then by other fields you decide as secondary sorting criteria.

