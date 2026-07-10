# Task042: create-ifc-project-structure

**Goal**: 创建完整的 IFC 项目骨架（Project→Site→Building→Storey）

**Input**: Empty or minimal IFC
**Output**: IFC with full project hierarchy
**Constraint**: Must have IfcProject, IfcSite, IfcBuilding, at least 1 IfcBuildingStorey
**Affected Classes**: IfcProject, IfcSite, IfcBuilding, IfcBuildingStorey
**Difficulty**: 2/5
**Frequency**: High
**Business Value**: 9/10
**Source**: IfcOpenHouse generate house tutorial; buildingSMART PCERT

## Description

*Real-world task derived from IfcOpenHouse generate house tutorial; buildingSMART PCERT. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
