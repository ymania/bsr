# Task046: check-ifc-material-assignment

**Goal**: 验证所有物理元素有材质

**Input**: IFC with elements missing material
**Output**: Report listing non-material elements
**Constraint**: Each physical element should have IfcMaterial
**Affected Classes**: IfcWall, IfcSlab, IfcBeam, IfcColumn
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 8/10
**Source**: BIMTester common rules; material passport

## Description

*Real-world task derived from BIMTester common rules; material passport. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
