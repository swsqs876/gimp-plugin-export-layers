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
  
  @classmethod
  def add_constraint(cls, constraints, constraint):
    cls._constraints_and_models[constraints].append(cls._get_row(constraint))
  
  @classmethod
  def reorder_constraint(cls, constraints, constraint, previous_position, new_position):
    if previous_position >= cls._DEFAULT_VALUE_INDEX:
      previous_position += 1
    
    if new_position >= cls._DEFAULT_VALUE_INDEX:
      new_position += 1
    
    model = cls._constraints_and_models[constraints]
    
    if new_position >= previous_position:
      model.move_after(model[previous_position].iter, model[new_position].iter)
    else:
      model.move_before(model[previous_position].iter, model[new_position].iter)
  
  @classmethod
  def remove_constraint(cls, constraints, constraint):
    model = cls._constraints_and_models[constraints]
    constraint_position = next(
      (i for i, row in enumerate(model)
       if row[cls._COLUMN_CONSTRAINT[0]] == constraint),
      None)
    
    if constraint_position is not None:
      del model[constraint_position]
  
  def clear_constraints(self, constraints):
    self._constraints_and_models[constraints].clear()
    self._fill_combo_box_model(self._constraints_and_models[constraints])
  
  def set_constraints(self, constraints, element=None):
    if constraints not in self._constraints_and_models:
      self._constraints_and_models[constraints] = self._get_combo_box_model()
      self._set_default_row_display_name()
    
    self._list_store = self._constraints_and_models[constraints]
    
    if element is None:
      element = self._element
    
    element.set_model(self._list_store)
  
  def _create_gui_element(self, setting):
    self._list_store = None
    
    combo_box = gtk.ComboBox()
    cell_renderer = gtk.CellRendererText()
    
    combo_box.pack_start(cell_renderer, expand=True)
    combo_box.add_attribute(cell_renderer, "text", self._COLUMN_DISPLAY_NAME[0])
    
    self.set_constraints(self._setting.constraints, combo_box)
    
    return combo_box
  
  def _get_value(self):
    index = self._element.get_active()
    
    if index == -1:
      return self._setting.default_value
    
    constraint = self._list_store[index][self._COLUMN_CONSTRAINT[0]]
    
    if constraint is not None:
      return constraint.name
    else:
      return self._setting.default_value
  
  def _set_value(self, value):
    constraint_index = self._DEFAULT_VALUE_INDEX
    
    for index, row in enumerate(self._list_store):
      constraint = row[self._COLUMN_CONSTRAINT[0]]
      if constraint is not None and constraint.name == value:
        constraint_index = index
        break
    
    self._element.set_active(constraint_index)
  
  def _get_combo_box_model(self):
    list_store = gtk.ListStore(*[column[1] for column in self._COLUMNS])
    self._fill_combo_box_model(list_store)
    return list_store
  
  def _fill_combo_box_model(self, list_store):
    list_store.append(self._get_default_row())
    for constraint in self._setting.constraints_iter:
      list_store.append(self._get_row(constraint))
  
  @staticmethod
  def _get_row(constraint):
    return [constraint, constraint["display_name"].value]
  
  @staticmethod
  def _get_default_row():
    return [None, ""]
  
  def _set_default_row_display_name(self):
    self._list_store[self._COLUMN_CONSTRAINT[0]][1] = (
      self._setting.default_value_display_name)
