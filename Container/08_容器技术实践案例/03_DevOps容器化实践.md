    # DevOps容器化实践

## 目录

- [DevOps容器化实践](#devops容器化实践)
  - [1. DevOps概述](#1-devops概述)
    - [1.1 DevOps理念](#11-devops理念)
    - [1.2 容器化DevOps优势](#12-容器化devops优势)
  - [2. CI/CD流水线设计](#2-cicd流水线设计)
    - [2.1 流水线架构](#21-流水线架构)
    - [2.2 流水线阶段](#22-流水线阶段)
  - [3. 容器化CI/CD](#3-容器化cicd)
    - [3.1 Jenkins流水线](#31-jenkins流水线)
    - [3.2 GitLab CI配置](#32-gitlab-ci配置)
- [.gitlab-ci.yml](#gitlab-ciyml)
    - [3.3 GitHub Actions](#33-github-actions)
- [.github/workflows/ci-cd.yml](#githubworkflowsci-cdyml)
  - [4. 自动化测试](#4-自动化测试)
    - [4.1 单元测试](#41-单元测试)
    - [4.2 集成测试](#42-集成测试)
    - [4.3 端到端测试](#43-端到端测试)
  - [5. 部署自动化](#5-部署自动化)
    - [5.1 蓝绿部署](#51-蓝绿部署)
- [蓝绿部署配置](#蓝绿部署配置)
    - [5.2 金丝雀部署](#52-金丝雀部署)
- [金丝雀部署配置](#金丝雀部署配置)
    - [5.3 自动回滚](#53-自动回滚)
- [自动回滚配置](#自动回滚配置)
  - [6. 监控与反馈](#6-监控与反馈)
    - [6.1 部署监控](#61-部署监控)
- [部署监控配置](#部署监控配置)
    - [6.2 性能监控](#62-性能监控)
- [性能监控配置](#性能监控配置)
    - [6.3 反馈机制](#63-反馈机制)
- [反馈机制配置](#反馈机制配置)
  - [7. 安全集成](#7-安全集成)
    - [7.1 代码扫描](#71-代码扫描)
- [代码扫描配置](#代码扫描配置)
    - [7.2 镜像扫描](#72-镜像扫描)
- [镜像扫描配置](#镜像扫描配置)
    - [7.3 安全策略](#73-安全策略)
- [安全策略配置](#安全策略配置)
  - [8. 实践案例](#8-实践案例)
    - [8.1 微服务CI/CD](#81-微服务cicd)
- [微服务CI/CD配置](#微服务cicd配置)
    - [8.2 多环境部署](#82-多环境部署)
- [多环境部署配置](#多环境部署配置)
  - [9. 最佳实践](#9-最佳实践)
    - [9.1 流水线设计原则](#91-流水线设计原则)
    - [9.2 容器化最佳实践](#92-容器化最佳实践)
    - [9.3 部署最佳实践](#93-部署最佳实践)
    - [9.4 团队协作](#94-团队协作)

- [DevOps容器化实践](#devops容器化实践)
  - [1. DevOps概述](#1-devops概述)
    - [1.1 DevOps理念](#11-devops理念)
    - [1.2 容器化DevOps优势](#12-容器化devops优势)
  - [2. CI/CD流水线设计](#2-cicd流水线设计)
    - [2.1 流水线架构](#21-流水线架构)
    - [2.2 流水线阶段](#22-流水线阶段)
  - [3. 容器化CI/CD](#3-容器化cicd)
    - [3.1 Jenkins流水线](#31-jenkins流水线)
    - [3.2 GitLab CI配置](#32-gitlab-ci配置)
- [.gitlab-ci.yml](#gitlab-ciyml)
    - [3.3 GitHub Actions](#33-github-actions)
- [.github/workflows/ci-cd.yml](#githubworkflowsci-cdyml)
  - [4. 自动化测试](#4-自动化测试)
    - [4.1 单元测试](#41-单元测试)
    - [4.2 集成测试](#42-集成测试)
    - [4.3 端到端测试](#43-端到端测试)
  - [5. 部署自动化](#5-部署自动化)
    - [5.1 蓝绿部署](#51-蓝绿部署)
- [蓝绿部署配置](#蓝绿部署配置)
    - [5.2 金丝雀部署](#52-金丝雀部署)
- [金丝雀部署配置](#金丝雀部署配置)
    - [5.3 自动回滚](#53-自动回滚)
- [自动回滚配置](#自动回滚配置)
- [检查部署状态](#检查部署状态)
- [发送告警](#发送告警)
  - [6. 监控与反馈](#6-监控与反馈)
    - [6.1 部署监控](#61-部署监控)
- [部署监控配置](#部署监控配置)
- [监控部署状态](#监控部署状态)
- [检查Pod状态](#检查pod状态)
- [检查服务状态](#检查服务状态)
- [检查Ingress状态](#检查ingress状态)
- [检查资源使用情况](#检查资源使用情况)
    - [6.2 性能监控](#62-性能监控)
- [性能监控配置](#性能监控配置)
- [性能监控脚本](#性能监控脚本)
- [检查响应时间](#检查响应时间)
- [检查错误率](#检查错误率)
- [检查吞吐量](#检查吞吐量)
    - [6.3 反馈机制](#63-反馈机制)
- [反馈机制配置](#反馈机制配置)
- [反馈系统脚本](#反馈系统脚本)
- [发送到Slack](#发送到slack)
- [发送到邮件](#发送到邮件)
- [发送到钉钉](#发送到钉钉)
  - [7. 安全集成](#7-安全集成)
    - [7.1 代码扫描](#71-代码扫描)
- [代码扫描配置](#代码扫描配置)
- [代码扫描脚本](#代码扫描脚本)
- [SonarQube扫描](#sonarqube扫描)
- [安全漏洞扫描](#安全漏洞扫描)
- [依赖扫描](#依赖扫描)
    - [7.2 镜像扫描](#72-镜像扫描)
- [镜像扫描配置](#镜像扫描配置)
- [镜像扫描脚本](#镜像扫描脚本)
- [Trivy扫描](#trivy扫描)
- [检查高危漏洞](#检查高危漏洞)
    - [7.3 安全策略](#73-安全策略)
- [安全策略配置](#安全策略配置)
  - [8. 实践案例](#8-实践案例)
    - [8.1 微服务CI/CD](#81-微服务cicd)
- [微服务CI/CD配置](#微服务cicd配置)
    - [8.2 多环境部署](#82-多环境部署)
- [多环境部署配置](#多环境部署配置)
- [多环境部署脚本](#多环境部署脚本)
- [更新环境配置](#更新环境配置)
- [更新镜像](#更新镜像)
- [等待部署完成](#等待部署完成)
- [验证部署](#验证部署)
- [部署到各个环境](#部署到各个环境)
  - [9. 最佳实践](#9-最佳实践)
    - [9.1 流水线设计原则](#91-流水线设计原则)
    - [9.2 容器化最佳实践](#92-容器化最佳实践)
    - [9.3 部署最佳实践](#93-部署最佳实践)
    - [9.4 团队协作](#94-团队协作)

- [DevOps容器化实践](#devops容器化实践)
  - [1. DevOps概述](#1-devops概述)
  - [2. CI/CD流水线设计](#2-cicd流水线设计)
  - [3. 容器化CI/CD](#3-容器化cicd)
  - [4. 自动化测试](#4-自动化测试)
  - [5. 部署自动化](#5-部署自动化)
  - [6. 监控与反馈](#6-监控与反馈)
  - [7. 安全集成](#7-安全集成)
  - [8. 实践案例](#8-实践案例)
  - [9. 最佳实践](#9-最佳实践)

## 1. DevOps概述

### 1.1 DevOps理念

- **文化变革**: 开发与运维团队协作
- **自动化**: 自动化构建、测试、部署
- **持续改进**: 持续集成、持续部署
- **快速反馈**: 快速反馈和迭代

### 1.2 容器化DevOps优势

- **环境一致性**: 开发、测试、生产环境一致
- **快速部署**: 容器化应用快速部署
- **资源隔离**: 应用间资源隔离
- **可扩展性**: 易于水平扩展

## 2. CI/CD流水线设计

### 2.1 流水线架构

```text
┌─────────────────────────────────────────────────────────────┐
│                    代码仓库                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Git       │  │   GitHub    │  │   GitLab    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD平台                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Jenkins   │  │   GitLab CI │  │   GitHub    │         │
│  │             │  │             │  │   Actions   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    容器平台                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Docker    │  │ Kubernetes  │  │   Registry  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 流水线阶段

1. **代码提交**: 开发者提交代码
2. **构建**: 编译和构建应用
3. **测试**: 自动化测试
4. **镜像构建**: 构建Docker镜像
5. **部署**: 部署到目标环境
6. **验证**: 部署后验证

## 3. 容器化CI/CD

### 3.1 Jenkins流水线

```groovy
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'registry.example.com'
        IMAGE_NAME = 'myapp'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'target/surefire-reports/*.xml'
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                script {
                    def image = docker.build("${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}")
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh "kubectl set image deployment/myapp myapp=${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
                sh "kubectl rollout status deployment/myapp"
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

### 3.2 GitLab CI配置

```yaml
    # .gitlab-ci.yml
stages:
  - build
  - test
  - docker-build
  - deploy

variables:
  DOCKER_REGISTRY: registry.example.com
  IMAGE_NAME: myapp

build:
  stage: build
  image: maven:3.8.4-openjdk-11
  script:
    - mvn clean package -DskipTests
  artifacts:
    paths:
      - target/*.jar

test:
  stage: test
  image: maven:3.8.4-openjdk-11
  script:
    - mvn test
  artifacts:
    reports:
      junit: target/surefire-reports/*.xml

docker-build:
  stage: docker-build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA
    - docker tag $DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA $DOCKER_REGISTRY/$IMAGE_NAME:latest
    - docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
  only:
    - main

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl set image deployment/myapp myapp=$DOCKER_REGISTRY/$IMAGE_NAME:$CI_COMMIT_SHA
    - kubectl rollout status deployment/myapp
  only:
    - main
```

### 3.3 GitHub Actions

```yaml
    # .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Build with Maven
      run: mvn clean package -DskipTests
    
    - name: Run tests
      run: mvn test
    
    - name: Build Docker image
      run: docker build -t myapp:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push myapp:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
        kubectl rollout status deployment/myapp
```

## 4. 自动化测试

### 4.1 单元测试

```java
// 单元测试示例
@SpringBootTest
class UserServiceTest {
    
    @MockBean
    private UserRepository userRepository;
    
    @Autowired
    private UserService userService;
    
    @Test
    void testCreateUser() {
        // Given
        User user = new User("john", "john@example.com");
        when(userRepository.save(any(User.class))).thenReturn(user);
        
        // When
        User result = userService.createUser(user);
        
        // Then
        assertThat(result.getName()).isEqualTo("john");
        assertThat(result.getEmail()).isEqualTo("john@example.com");
    }
}
```

### 4.2 集成测试

```java
// 集成测试示例
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserControllerIntegrationTest {
    
    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    void testCreateUser() {
        // Given
        User user = new User("john", "john@example.com");
        
        // When
        ResponseEntity<User> response = restTemplate.postForEntity("/users", user, User.class);
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getName()).isEqualTo("john");
    }
}
```

### 4.3 端到端测试

```javascript
// 端到端测试示例
describe('User Management', () => {
  beforeEach(() => {
    cy.visit('/users');
  });
  
  it('should create a new user', () => {
    cy.get('[data-testid="create-user-button"]').click();
    cy.get('[data-testid="user-name-input"]').type('John Doe');
    cy.get('[data-testid="user-email-input"]').type('john@example.com');
    cy.get('[data-testid="save-button"]').click();
    
    cy.get('[data-testid="user-list"]').should('contain', 'John Doe');
  });
  
  it('should edit an existing user', () => {
    cy.get('[data-testid="edit-user-button"]').first().click();
    cy.get('[data-testid="user-name-input"]').clear().type('Jane Doe');
    cy.get('[data-testid="save-button"]').click();
    
    cy.get('[data-testid="user-list"]').should('contain', 'Jane Doe');
  });
});
```

## 5. 部署自动化

### 5.1 蓝绿部署

```yaml
    # 蓝绿部署配置
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp-rollout
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: myapp-active
      previewService: myapp-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: myapp-preview
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8080
```

### 5.2 金丝雀部署

```yaml
    # 金丝雀部署配置
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp-canary
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
      canaryService: myapp-canary
      stableService: myapp-stable
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8080
```

### 5.3 自动回滚

```yaml
    # 自动回滚配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: auto-rollback
data:
  rollback.sh: |
    #!/bin/bash
    # 检查部署状态
    if ! kubectl rollout status deployment/myapp --timeout=300s; then
      echo "Deployment failed, rolling back..."
      kubectl rollout undo deployment/myapp
      kubectl rollout status deployment/myapp --timeout=300s
      
      if [ $? -eq 0 ]; then
        echo "Rollback successful"
      else
        echo "Rollback failed"
        # 发送告警
        curl -X POST http://alertmanager:9093/api/v1/alerts \
          -d '[{"labels":{"alertname":"RollbackFailed","deployment":"myapp"}}]'
      fi
    fi
```

## 6. 监控与反馈

### 6.1 部署监控

```yaml
    # 部署监控配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: deployment-monitor
data:
  monitor.sh: |
    #!/bin/bash
    # 监控部署状态
    monitor_deployment() {
      local deployment=$1
      local namespace=$2
      
      echo "Monitoring deployment $deployment in namespace $namespace"
      
      # 检查Pod状态
      kubectl get pods -n $namespace -l app=$deployment
      
      # 检查服务状态
      kubectl get svc -n $namespace -l app=$deployment
      
      # 检查Ingress状态
      kubectl get ingress -n $namespace -l app=$deployment
      
      # 检查资源使用情况
      kubectl top pods -n $namespace -l app=$deployment
    }
    
    monitor_deployment "myapp" "default"
```

### 6.2 性能监控

```yaml
    # 性能监控配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: performance-monitor
data:
  monitor.sh: |
    #!/bin/bash
    # 性能监控脚本
    monitor_performance() {
      local service=$1
      local endpoint=$2
      
      echo "Monitoring performance of $service"
      
      # 检查响应时间
      response_time=$(curl -o /dev/null -s -w '%{time_total}' $endpoint)
      echo "Response time: ${response_time}s"
      
      # 检查错误率
      error_count=$(curl -s $endpoint/metrics | grep 'http_requests_total{status="5.."}' | awk '{print $2}')
      total_count=$(curl -s $endpoint/metrics | grep 'http_requests_total' | awk '{sum+=$2} END {print sum}')
      error_rate=$(echo "scale=2; $error_count * 100 / $total_count" | bc)
      echo "Error rate: ${error_rate}%"
      
      # 检查吞吐量
      throughput=$(curl -s $endpoint/metrics | grep 'http_requests_total' | awk '{sum+=$2} END {print sum}')
      echo "Throughput: $throughput requests"
    }
    
    monitor_performance "myapp" "http://myapp:8080"
```

### 6.3 反馈机制

```yaml
    # 反馈机制配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: feedback-system
data:
  feedback.sh: |
    #!/bin/bash
    # 反馈系统脚本
    send_feedback() {
      local status=$1
      local message=$2
      
      # 发送到Slack
      curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"Deployment $status: $message\"}" \
        $SLACK_WEBHOOK_URL
      
      # 发送到邮件
      echo "$message" | mail -s "Deployment $status" $EMAIL_RECIPIENTS
      
      # 发送到钉钉
      curl -X POST -H 'Content-type: application/json' \
        --data "{\"msgtype\":\"text\",\"text\":{\"content\":\"Deployment $status: $message\"}}" \
        $DINGTALK_WEBHOOK_URL
    }
    
    send_feedback "SUCCESS" "Deployment completed successfully"
```

## 7. 安全集成

### 7.1 代码扫描

```yaml
    # 代码扫描配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: code-scan
data:
  scan.sh: |
    #!/bin/bash
    # 代码扫描脚本
    scan_code() {
      local project_path=$1
      
      echo "Scanning code in $project_path"
      
      # SonarQube扫描
      sonar-scanner \
        -Dsonar.projectKey=myapp \
        -Dsonar.sources=$project_path \
        -Dsonar.host.url=$SONARQUBE_URL \
        -Dsonar.login=$SONARQUBE_TOKEN
      
      # 安全漏洞扫描
      npm audit --audit-level moderate
      
      # 依赖扫描
      snyk test
    }
    
    scan_code "/app"
```

### 7.2 镜像扫描

```yaml
    # 镜像扫描配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-scan
data:
  scan.sh: |
    #!/bin/bash
    # 镜像扫描脚本
    scan_image() {
      local image=$1
      
      echo "Scanning image $image"
      
      # Trivy扫描
      trivy image --format json --output scan-results.json $image
      
      # 检查高危漏洞
      high_vulns=$(jq '.Results[].Vulnerabilities[] | select(.Severity == "HIGH")' scan-results.json | jq -s 'length')
      
      if [ $high_vulns -gt 0 ]; then
        echo "Found $high_vulns high severity vulnerabilities"
        exit 1
      fi
      
      echo "No high severity vulnerabilities found"
    }
    
    scan_image "myapp:latest"
```

### 7.3 安全策略

```yaml
    # 安全策略配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-policy
data:
  policy.yaml: |
    apiVersion: v1
    kind: PodSecurityPolicy
    metadata:
      name: restricted
    spec:
      privileged: false
      allowPrivilegeEscalation: false
      requiredDropCapabilities:
        - ALL
      volumes:
        - 'configMap'
        - 'emptyDir'
        - 'projected'
        - 'secret'
        - 'downwardAPI'
        - 'persistentVolumeClaim'
      runAsUser:
        rule: 'MustRunAsNonRoot'
      seLinux:
        rule: 'RunAsAny'
      fsGroup:
        rule: 'RunAsAny'
```

## 8. 实践案例

### 8.1 微服务CI/CD

```yaml
    # 微服务CI/CD配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: microservice-cicd
data:
  pipeline.yaml: |
    stages:
      - build
      - test
      - security-scan
      - docker-build
      - deploy
    
    variables:
      DOCKER_REGISTRY: registry.example.com
      SERVICES: "user-service product-service order-service"
    
    build:
      stage: build
      script:
        - for service in $SERVICES; do
            mvn -f $service/pom.xml clean package -DskipTests;
          done
    
    test:
      stage: test
      script:
        - for service in $SERVICES; do
            mvn -f $service/pom.xml test;
          done
    
    security-scan:
      stage: security-scan
      script:
        - for service in $SERVICES; do
            sonar-scanner -Dsonar.projectKey=$service;
          done
    
    docker-build:
      stage: docker-build
      script:
        - for service in $SERVICES; do
            docker build -t $DOCKER_REGISTRY/$service:$CI_COMMIT_SHA $service/;
            docker push $DOCKER_REGISTRY/$service:$CI_COMMIT_SHA;
          done
    
    deploy:
      stage: deploy
      script:
        - for service in $SERVICES; do
            kubectl set image deployment/$service $service=$DOCKER_REGISTRY/$service:$CI_COMMIT_SHA;
            kubectl rollout status deployment/$service;
          done
```

### 8.2 多环境部署

```yaml
    # 多环境部署配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: multi-env-deploy
data:
  deploy.sh: |
    #!/bin/bash
    # 多环境部署脚本
    deploy_to_env() {
      local env=$1
      local image_tag=$2
      
      echo "Deploying to $env environment"
      
      # 更新环境配置
      kubectl set env deployment/myapp ENVIRONMENT=$env -n $env
      
      # 更新镜像
      kubectl set image deployment/myapp myapp=myapp:$image_tag -n $env
      
      # 等待部署完成
      kubectl rollout status deployment/myapp -n $env --timeout=300s
      
      # 验证部署
      kubectl get pods -n $env -l app=myapp
    }
    
    # 部署到各个环境
    deploy_to_env "dev" "latest"
    deploy_to_env "staging" "v1.0.0"
    deploy_to_env "prod" "v1.0.0"
```

## 9. 最佳实践

### 9.1 流水线设计原则

1. **快速反馈**: 快速反馈构建和测试结果
2. **并行执行**: 并行执行独立的任务
3. **失败快速**: 快速失败，避免浪费资源
4. **可重复性**: 确保流水线的可重复性

### 9.2 容器化最佳实践

1. **多阶段构建**: 使用多阶段构建优化镜像
2. **镜像优化**: 优化镜像大小和层数
3. **安全扫描**: 集成安全扫描到流水线
4. **版本管理**: 使用语义化版本管理

### 9.3 部署最佳实践

1. **渐进式部署**: 使用蓝绿或金丝雀部署
2. **自动回滚**: 实现自动回滚机制
3. **健康检查**: 配置健康检查
4. **监控告警**: 建立监控和告警机制

### 9.4 团队协作

1. **代码审查**: 实施代码审查流程
2. **文档管理**: 维护完善的文档
3. **知识分享**: 定期进行知识分享
4. **持续改进**: 持续改进流程和工具
