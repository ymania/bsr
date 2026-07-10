# Task044: assign-system-to-mep

**Goal**: 将 MEP 设备分配到 IfcSystem

**Input**: IFC with unassigned MEP elements
**Output**: IFC with each MEP element in a system
**Constraint**: Each flow element should be in IfcDistributionSystem
**Affected Classes**: IfcFlowTerminal, IfcFlowSegment, IfcDistributionSystem
**Difficulty**: 2/5
**Frequency**: Medium
**Business Value**: 7/10
**Source**: buildingSMART IFC4 MEP; system assignment

## Description

*Real-world task derived from buildingSMART IFC4 MEP; system assignment. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
