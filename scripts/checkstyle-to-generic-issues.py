#!/usr/bin/env python3
"""
Convierte el reporte XML de Checkstyle al formato Generic Issue Data de SonarQube.
Uso: python3 checkstyle-to-generic-issues.py <checkstyle.xml> [output.json]
"""
import json
import re
import sys
import xml.etree.ElementTree as ET

ENGINE_ID = "checkstyle"

# Mapeo Checkstyle severity -> SonarQube (Standard Experience)
SEVERITY_MAP = {
    "error": "MAJOR",
    "warning": "MINOR",
    "info": "INFO",
}

# Mapeo para impacts (MQR): BLOCKER, HIGH, MEDIUM, LOW, INFO
IMPACT_SEVERITY_MAP = {
    "BLOCKER": "BLOCKER",
    "CRITICAL": "HIGH",
    "MAJOR": "MEDIUM",
    "MINOR": "LOW",
    "INFO": "INFO",
}


def _to_impact_severity(standard_severity: str) -> str:
    return IMPACT_SEVERITY_MAP.get(standard_severity, "MEDIUM")


def extract_rule_id(source: str) -> str:
    """Extrae un ruleId corto del source de Checkstyle (ej: UnusedImportsCheck -> UnusedImports)."""
    if not source:
        return "Unknown"
    parts = source.split(".")
    name = parts[-1] if parts else "Unknown"
    return re.sub(r"Check$", "", name)


def to_relative_path(file_path: str) -> str:
    """Convierte path absoluto a relativo respecto al proyecto (ej: src/main/java/...)."""
    path = file_path
    # Buscar src/ para obtener la ruta relativa al proyecto
    for needle in ["/src/", "src/", "/src\\", "src\\"]:
        idx = path.find(needle)
        if idx >= 0:
            return path[idx:] if path[idx] == "s" else path[idx + 1:]
    # Si es relativo, devolver tal cual
    return path


def convert(checkstyle_path: str, output_path: str) -> None:
    tree = ET.parse(checkstyle_path)
    root = tree.getroot()

    rules_seen = {}  # rule_id -> rule_obj
    issues = []

    for file_elem in root.findall("file"):
        file_name = file_elem.get("name", "")
        rel_path = to_relative_path(file_name)

        for error in file_elem.findall("error"):
            line = int(error.get("line", 1))
            col = error.get("column", "1")
            msg = error.get("message", "")
            severity_in = (error.get("severity") or "warning").lower()
            source = error.get("source", "")

            rule_id = extract_rule_id(source)
            severity = SEVERITY_MAP.get(severity_in, "MINOR")

            if rule_id not in rules_seen:
                impact_sev = _to_impact_severity(severity)
                rules_seen[rule_id] = {
                    "id": rule_id,
                    "name": f"Checkstyle: {rule_id}",
                    "description": f"Checkstyle rule {rule_id}",
                    "engineId": ENGINE_ID,
                    "cleanCodeAttribute": "FORMATTED",
                    "type": "CODE_SMELL",
                    "impacts": [{"softwareQuality": "MAINTAINABILITY", "severity": impact_sev}],
                }

            text_range = {"startLine": line}
            if col and col != "0":
                text_range["startColumn"] = int(col)

            issues.append({
                "ruleId": rule_id,
                "primaryLocation": {
                    "message": msg,
                    "filePath": rel_path,
                    "textRange": text_range,
                },
            })

    report = {
        "rules": list(rules_seen.values()),
        "issues": issues,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return len(issues)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: checkstyle-to-generic-issues.py <checkstyle.xml> [output.json]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "sonar-external-issues.json"
    count = convert(input_path, output_path)
    print(f"Generado: {output_path} ({count} issues)")
