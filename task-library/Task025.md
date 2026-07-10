# Task025: add-pset-fire-rating

**Goal**: 为所有 IfcWall/IfcSlab 添加标准化 Pset_WallCommon.FireRating

**Input**: IFC without fire rating properties
**Output**: IFC with FireRating on all fire-rated elements
**Constraint**: FireRating must be 0.5HR/1HR/2HR/4HR
**Affected Classes**: IfcWall, IfcSlab, IfcPropertySet
**Difficulty**: 2/5
**Frequency**: High
**Business Value**: 9/10
**Source**: IfcOpenShell api.pset example; buildingSMART IFC4 property sets

## Description

*Real-world task derived from IfcOpenShell api.pset example; buildingSMART IFC4 property sets. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
