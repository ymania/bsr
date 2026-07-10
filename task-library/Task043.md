# Task043: check-duct-connectivity

**Goal**: 验证 IfcFlowSegment 连接性

**Input**: MEP IFC with disconnected ducts
**Output**: Report listing disconnected segments
**Constraint**: Each duct must be connected to at least 2 fittings or terminals
**Affected Classes**: IfcFlowSegment, IfcFlowFitting
**Difficulty**: 3/5
**Frequency**: Medium
**Business Value**: 7/10
**Source**: RWTH DigitalHub HVAC; MEP validation

## Description

*Real-world task derived from RWTH DigitalHub HVAC; MEP validation. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
