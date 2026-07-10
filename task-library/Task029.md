# Task029: copy-properties-from-type

**Goal**: 将 IfcType 的属性复制到所有实例

**Input**: IFC with properties only on type, not instances
**Output**: IFC where each instance inherits type properties
**Constraint**: Instance properties must not conflict with type
**Affected Classes**: All IfcElement, IfcType
**Difficulty**: 3/5
**Frequency**: Medium
**Business Value**: 7/10
**Source**: xbim issue: type properties not exporting to IFC; Revit export workaround

## Description

*Real-world task derived from xbim issue: type properties not exporting to IFC; Revit export workaround. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
