# Task050: check-beam-column-connectivity

**Goal**: 验证梁柱节点连接

**Input**: IFC structural model
**Output**: Report listing disconnected beam-column joints
**Constraint**: Each beam end must connect to a column or wall
**Affected Classes**: IfcBeam, IfcColumn, IfcRelConnectsElements
**Difficulty**: 3/5
**Frequency**: Low
**Business Value**: 7/10
**Source**: KIT structural IFC examples; structural validation

## Description

*Real-world task derived from KIT structural IFC examples; structural validation. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
