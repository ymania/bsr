# Task049: extract-space-boundaries

**Goal**: 提取 IfcSpace 的 IfcRelSpaceBoundary 拓扑关系

**Input**: IFC with spaces
**Output**: JSON listing each room's bounding walls/doors/windows
**Constraint**: N/A — read-only
**Affected Classes**: IfcSpace, IfcRelSpaceBoundary
**Difficulty**: 2/5
**Frequency**: Low
**Business Value**: 7/10
**Source**: buildingSMART space boundary example; HITOS model analysis

## Description

*Real-world task derived from buildingSMART space boundary example; HITOS model analysis. 
Uses only existing Operations (ModifyProperty, SelectElement, SelectByType).
No new Runtime capabilities required.*
