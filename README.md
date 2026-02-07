# cicd-templates

Templates reutilizables de CI/CD para pipelines en GitHub Actions.

## Workflows disponibles

### quality-gate.yml

Pipeline de calidad: lint (Checkstyle), unit tests y SonarQube. Convierte el reporte de Checkstyle al formato Generic Issue Data (JSON) para que SonarQube muestre los issues con la etiqueta del linter (checkstyle).

**Secrets:**
- `SONAR_HOST_URL` - URL del servidor SonarQube
- `SONAR_TOKEN` - Token de SonarQube

**Inputs:**
- `java_version` (opcional) - Versión Java (default: 21)
- `checkstyle_report_path` (opcional) - Ruta del XML de Checkstyle (default: target/checkstyle-result.xml)
- `coverage_report_path` (opcional) - Ruta del XML de JaCoCo (default: target/site/jacoco/jacoco.xml)
- `templates_repo` (opcional) - Repo de templates para el script de conversión (default: sergioortiz17/cicd-templates)

### java-lint.yml

Ejecuta Checkstyle y sube el reporte como artifact para que SonarQube lo consuma.

### java-test.yml

Ejecuta unit tests (mvn test) y sube el reporte de cobertura Jacoco como artifact.

### ecs-build-deploy.yml

Pipeline para construir imagen Docker, subirla a Amazon ECR y desplegar en ECS.

**Inputs:**
- `app_name` (requerido): Nombre de la aplicación
- `ecr_repository` (requerido): Nombre del repositorio ECR
- `ecs_cluster` (requerido): Nombre del cluster ECS
- `ecs_service` (requerido): Nombre del servicio ECS
- `aws_region` (opcional): Región AWS (default: us-east-1)

**Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Uso

Desde otro repositorio (ej: java-cdk-tools-dev):

```yaml
jobs:
  deploy:
    uses: TU_ORG/cicd-templates/.github/workflows/ecs-build-deploy.yml@main
    with:
      app_name: mi-app
      ecr_repository: mi-app
      ecs_cluster: mi-cluster
      ecs_service: mi-servicio
    secrets:
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Requisitos

- El repositorio que llama debe tener un Dockerfile en la raíz
- La infraestructura ECR y ECS debe existir (desplegada con infralive)
