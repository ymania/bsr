# Task041: assign-element-to-storey

**Goal**: 将游离元素分配到合适的楼层

**Input**: IFC with orphans not in any storey
**Output**: IFC with all elements in a storey
**Constraint**: Each element assigned to closest storey by Z
**Affected Classes**: All IfcBuildingElement
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 8/10
**Source**: IfcOpenShell spatial.assign_container; common BIM issue

## Description

*Real-world task derived from IfcOpenShell spatial.assign_container; common BIM issue. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
