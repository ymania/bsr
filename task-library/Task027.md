# Task027: add-qto-wall-quantities

**Goal**: 为 IfcWall 添加标准面积/体积/长度量

**Input**: IFC walls without quantity take-off data
**Output**: IFC with Qto_WallBaseQuantities populated
**Constraint**: Quantities must have valid measure values
**Affected Classes**: IfcWall, IfcQuantityArea, IfcQuantityLength
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 8/10
**Source**: IfcOpenShell api.pset.add_qto; QTO standard

## Description

*Real-world task derived from IfcOpenShell api.pset.add_qto; QTO standard. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
