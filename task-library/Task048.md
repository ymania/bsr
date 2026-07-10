# Task048: check-reverse-attributes

**Goal**: 验证 IfcRel 的反向属性完整性

**Input**: IFC with relationships
**Output**: Report checking inverse attributes
**Constraint**: All IfcRelationship must have valid inverses
**Affected Classes**: All IfcRelationship
**Difficulty**: 3/5
**Frequency**: Low
**Business Value**: 6/10
**Source**: IfcOpenShell schema querying; inverse attribute validation

## Description

*Real-world task derived from IfcOpenShell schema querying; inverse attribute validation. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
