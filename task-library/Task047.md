# Task047: export-element-tree

**Goal**: 导出 IFC 实体树（父子关系嵌套层级）

**Input**: Any IFC file
**Output**: JSON tree of spatial containment hierarchy
**Constraint**: N/A — export only
**Affected Classes**: All entities
**Difficulty**: 2/5
**Frequency**: Low
**Business Value**: 7/10
**Source**: IfcOpenShell traverse() example; entity tree visualization

## Description

*Real-world task derived from IfcOpenShell traverse() example; entity tree visualization. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
