# Main Dashboard Wireframe Sketch

This document describes the visual layout and components of the Offensive Security Platform's main dashboard.

## Overall Layout (Dark Mode IDE)

```text
+-----------------------------------------------------------+
|  HEADER: Project: [Name] | User: [Admin] | Status: [Act]  |
+-------------------+---------------------------------------+
|                   |                                       |
|  LEFT SIDEBAR     |          CENTER PANEL                 |
|                   |                                       |
|  [PROJECTS]       |    +-----------------------------+    |
|  - Project X      |    |       KPI SUMMARY CARDS     |    |
|  - Firmware Audit |    | [TGT: 8] [VULN: 12] [SESS: 3] |    |
|                   |    +-----------------------------+    |
|  [TARGETS]        |                                       |
|  - 192.168.1.1    |    +-----------------------------+    |
|  - 192.168.1.50   |    |      RECENT ACTIVITY        |    |
|                   |    | - Vuln found in httpd       |    |
|  [MODULES]        |    | - New session established   |    |
|  - Binary Analysis|    +-----------------------------+    |
|  - Payloads       |                                       |
|  - Sessions       |    +-----------------------------+    |
|  - AI Assistant   |    |      RECENT FINDINGS        |    |
|                   |    | [Func] [Sev] [Date]         |    |
+-------------------+----+-----------------------------+----+
|                   |                                       |
|                   |          RIGHT SIDEBAR                |
|                   |                                       |
|                   |          [AI ANALYSIS]                |
|                   |          "Unsafe gets() found..."     |
|                   |                                       |
|                   |          [NOTES]                      |
|                   |          "Check libc version..."      |
|                   |                                       |
+-------------------+---------------------------------------+
```

## Detailed Component Breakdown

### 1. Header Bar
- **Project Context**: Displays the currently active project and its status (Planning, Active, Completed).
- **User Info**: Quick access to profile and notifications.

### 2. Navigation Sidebar (Left)
- **Projects**: Accordion list of engagements. Includes a "New Project" button.
- **Targets**: Live status indicators (Online/Offline) for devices in the current project.
- **Modules**: One-click access to the core functional areas of the tool.

### 3. Main Action Area (Center)
- **KPI Cards**: Real-time stats on findings, sessions, and targets.
- **Activity Feed**: Log of recent automated and manual actions.
- **Findings Table**: Sortable list of discovered vulnerabilities with severity color-coding.

### 4. Intelligence & Context Sidebar (Right)
- **AI Panel**: Context-sensitive AI analysis of the selected item (function, binary, etc.). Includes "Generate Exploit" buttons.
- **Notes/Metadata**: Quick edits for analyst notes and technical metadata.

## Visual Theme
- **Background**: Dark slate / Obsidian (#0f172a).
- **Accents**: Red for Critical, Orange for High, Purple for AI-driven insights.
- **Typography**: Monospace for code/memory addresses, clean sans-serif for UI.
