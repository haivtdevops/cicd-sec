FROM jenkins/jenkins:lts-jdk17

USER root

# Cài Python (cho Semgrep), Go (build/test app), unzip, curl, docker-cli để build/push image
# Không cài Semgrep ở build-time để tránh lỗi pip (network, registry) – sẽ cài trong pipeline.
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    python3 python3-pip golang-go unzip curl docker.io \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Cài sonar-scanner CLI cho SonarQube.
# Nếu download thất bại (mạng nội bộ hạn chế), build vẫn tiếp tục.
ARG SONAR_SCANNER_VERSION=5.0.1.3006
RUN set -eux; \
  url="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux-x64.zip"; \
  tmp="/tmp/sonar-scanner.zip"; \
  if curl -fsSL "$url" -o "$tmp"; then \
    unzip "$tmp" -d /opt; \
    mv /opt/sonar-scanner-* /opt/sonar-scanner; \
    ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner; \
    rm "$tmp"; \
  else \
    echo "WARNING: failed to download sonar-scanner CLI, SonarQube stage will be skipped if CLI missing."; \
  fi

# Cài Trivy cho image scanning
ARG TRIVY_VERSION=0.52.0
RUN set -eux; \
  url="https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz"; \
  tmp="/tmp/trivy.tar.gz"; \
  if curl -fsSL "$url" -o "$tmp"; then \
    tar -xzf "$tmp" -C /tmp trivy; \
    mv /tmp/trivy /usr/local/bin/trivy; \
    chmod +x /usr/local/bin/trivy; \
    rm "$tmp"; \
  else \
    echo "WARNING: failed to download Trivy, image scan stage will be skipped if Trivy missing."; \
  fi

# Alias python cho tiện (nếu chưa tồn tại)
RUN ln -s /usr/bin/python3 /usr/bin/python || true

USER jenkins

# Bỏ wizard lần đầu và tạo sẵn admin với password cố định
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false

# Groovy init script sẽ tạo user admin/@dmin@123!
COPY basic-security.groovy /usr/share/jenkins/ref/init.groovy.d/basic-security.groovy

WORKDIR /var/jenkins_home
