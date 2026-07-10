# Task040: add-ifc-building-storey

**Goal**: 如果不存在，创建 IfcBuildingStorey 层级

**Input**: IFC without storey hierarchy
**Output**: IFC with IfcBuildingStorey and IfcRelAggregates
**Constraint**: Project → Site → Building → Storey structure
**Affected Classes**: IfcBuildingStorey, IfcRelAggregates
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 8/10
**Source**: IfcOpenHouse tutorial; BIM spatial hierarchy requirement

## Description

*Real-world task derived from IfcOpenHouse tutorial; BIM spatial hierarchy requirement. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
