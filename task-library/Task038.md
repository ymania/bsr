# Task038: fix-broken-ifc-relationships

**Goal**: 检测并修复悬空的关系引用

**Input**: IFC with relationships pointing to deleted entities
**Output**: IFC with clean relationship graph
**Constraint**: All IfcRel* must reference existing entities
**Affected Classes**: All IfcRelationship
**Difficulty**: 3/5
**Frequency**: High
**Business Value**: 9/10
**Source**: xbim common issues; buildingSMART reference integrity

## Description

*Real-world task derived from xbim common issues; buildingSMART reference integrity. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
