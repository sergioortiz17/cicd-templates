# cicd-templates

Templates reutilizables de CI/CD para pipelines en GitHub Actions.

## Workflows disponibles

### quality-gate.yml

Pipeline de calidad: lint (Checkstyle), unit tests y SonarQube. Llama a java-lint.yml y java-test.yml, descarga los reportes y los pasa a SonarQube.

**Secrets:**
- `SONAR_HOST_URL` - URL del servidor SonarQube (ej: http://X.X.X.X:9000)
- `SONAR_TOKEN` - Token de SonarQube

**Inputs:**
- `java_version` (opcional) - Versión Java (default: 21)

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
