# Task037: fix-empty-property-values

**Goal**: 将空 Property 值填充为默认值 N/A

**Input**: IFC with empty property values
**Output**: IFC with all property values non-empty
**Constraint**: Empty properties should be set to N/A or —
**Affected Classes**: All IfcPropertySingleValue
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 7/10
**Source**: Revit IFC export: empty properties skipped (Issue #160); xbim workaround

## Description

*Real-world task derived from Revit IFC export: empty properties skipped (Issue #160); xbim workaround. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
