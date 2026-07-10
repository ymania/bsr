# Task028: add-qto-slab-quantities

**Goal**: 为 IfcSlab 添加标准量

**Input**: IFC slabs without quantity sets
**Output**: IFC with Qto_SlabBaseQuantities
**Constraint**: NetArea/NetVolume/Perimeter required
**Affected Classes**: IfcSlab, IfcQuantityArea
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 8/10
**Source**: IfcOpenShell qto example; quantity surveying

## Description

*Real-world task derived from IfcOpenShell qto example; quantity surveying. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
