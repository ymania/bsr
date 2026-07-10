# Task032: check-ifc-class-not-abstract

**Goal**: 验证没有实例化抽象实体

**Input**: IFC with abstract entity instances
**Output**: Report listing abstract violations
**Constraint**: No abstract IfcObject classes must be instantiated
**Affected Classes**: All entities
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 9/10
**Source**: buildingSMART validation service; EXPRESS schema rules

## Description

*Real-world task derived from buildingSMART validation service; EXPRESS schema rules. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
