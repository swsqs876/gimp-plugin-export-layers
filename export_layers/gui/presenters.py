# -*- coding: utf-8 -*-
#
# This file is part of Export Layers.
#
# Copyright (C) 2013-2019 khalim19 <khalim19@gmail.com>
#
# Export Layers is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Export Layers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Export Layers.  If not, see <https://www.gnu.org/licenses/>.

"""
This module defines GUI for custom `pg.setting.Setting` classes defined in the
plug-in.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from future.builtins import *

import pygtk
pygtk.require("2.0")
import gtk
import gobject

import gimpui

from export_layers import pygimplib as pg


class GimpObjectPlaceholdersComboBoxPresenter(pg.setting.GtkPresenter):
  """
  This class is a `setting.presenter.Presenter` subclass for
  `gimpui.IntComboBox` elements used for `placeholders.PlaceholderSetting`.
  
  Value: `placeholders.PlaceholderSetting` instance selected in the combo box.
  """
  
  _VALUE_CHANGED_SIGNAL = "changed"
  
  def _create_gui_element(self, setting):
    placeholder_names_and_values = []
    
    for index, placeholder in enumerate(setting.get_allowed_placeholders()):
      placeholder_names_and_values.extend(
        (placeholder.display_name.encode(pg.GTK_CHARACTER_ENCODING), index))
    
    return gimpui.IntComboBox(tuple(placeholder_names_and_values))
  
  def _get_value(self):
    return self._setting.get_allowed_placeholder_names()[self._element.get_active()]
  
  def _set_value(self, value):
    self._element.set_active(self._setting.get_allowed_placeholder_names().index(value))


class ConstraintComboBoxPresenter(pg.setting.GtkPresenter):
  """
  This class is a `setting.presenter.Presenter` subclass for `gtk.ComboBox`
  elements used for `operations.ConstraintSetting` instances.
  
  Value: Constraint name as string selected in the combo box.
  """
  
  _VALUE_CHANGED_SIGNAL = "changed"
  
  _COLUMNS = (_COLUMN_CONSTRAINT, _COLUMN_DISPLAY_NAME) = (
    [0, gobject.TYPE_PYOBJECT], [1, gobject.TYPE_STRING])
  
  _DEFAULT_VALUE_INDEX = 0
  
  _constraints_and_models = {}
  
  def set_constraints(self, constraints, element=None):
    if constraints not in self._constraints_and_models:
      self._constraints_and_models[constraints] = self._get_combo_box_model()
    
    self._list_store = self._constraints_and_models[constraints]
    
    if element is None:
      self._element.set_model(self._list_store)
    else:
      element.set_model(self._list_store)
  
  def add_constraint(self, constraints, constraint):
    self._constraints_and_models[constraints].append(self._get_row(constraint))
  
  def reorder_constraint(self, constraints, constraint, previous_position, new_position):
    model = self._constraints_and_models[constraints]
    model.move_after(model[previous_position].iter, model[new_position].iter)
  
  def remove_constraint(self, constraints, constraint):
    model = self._constraints_and_models[constraints]
    constraint_position = next(
      (i for i, row in enumerate(model) if row[0] == constraint), None)
    if constraint_position is not None:
      del model[constraint_position]
  
  def clear_constraints(self, constraints):
    self._constraints_and_models[constraints].clear()
  
  def _create_gui_element(self, setting):
    self._list_store = None
    
    combo_box = gtk.ComboBox()
    cell_renderer = gtk.CellRendererText()
    
    combo_box.pack_start(cell_renderer, expand=True)
    combo_box.add_attribute(cell_renderer, "text", self._COLUMN_DISPLAY_NAME[0])
    
    self.set_constraints(self._setting.constraints, combo_box)
    
    return combo_box
  
  def _get_value(self):
    return self._list_store[self._element.get_active()]
  
  def _set_value(self, value):
    index = next((row for row in range(len(self._list_store)) if row[0] == value), None)
    
    if index is not None:
      self._element.set_active(index)
    else:
      self._element.set_active(self._DEFAULT_VALUE_INDEX)
  
  def _get_combo_box_model(self):
    list_store = gtk.ListStore(self._COLUMN_DISPLAY_NAME[1])
    
    list_store.append(self._get_default_row())
    for constraint in self._setting.constraints_iter:
      list_store.append(self._get_row(constraint))
    
    return list_store
  
  def _get_row(self, constraint):
    return [constraint, constraint["display_name"].value]
  
  def _get_default_row(self):
    return [None, self._setting.default_value_display_name]
