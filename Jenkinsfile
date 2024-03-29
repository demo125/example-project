pipeline {
  agent {
    kubernetes {
        inheritFrom 'kaniko-pod-template'
    }
  }
  stages {
    // stage('build image') {
    //   steps {
    //     container('kaniko-container') {
    //         // sh 'executor'
    //         sh 'ls -la'
    //         sh "mkdir -p /kaniko/.docker"
    //         withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', passwordVariable: 'PASSWORD', usernameVariable: 'USER')]) {
    //             sh "echo '{\"auths\":{\"$DOCKER_REGISTRY_URL\":{\"username\":\"$USER\",\"password\":\"$PASSWORD\"}}}' > /kaniko/.docker/config.json"
    //             sh 'cat /kaniko/.docker/config.json'
    //             sh 'executor --context=git://github.com/demo125/example-project.git --dockerfile Dockerfile.dev --destination $DOCKER_REGISTRY_URL/example-project:$BUILD_NUMBER'
    //         }
    //     }
    //   }
    // }
    stage('update argocd deployment') {
      steps {
        checkout(
            [$class: 'GitSCM', 
            branches: [[name: '*/main']], 
            doGenerateSubmoduleConfigurations: false, 
            extensions: [[$class: 'CleanBeforeCheckout']], 
            submoduleCfg: [], 
            userRemoteConfigs: [[url: 'https://github.com/demo125/mlops-platform.git']]]
        )
        dir('dagster/base'){
          sh 'cat values.yaml | grep tag: '
          script {
              sh """
                  sed -i -E 's/(tag:[ ])[0-9]+([ ]+# SED-ANCHOR-DAGSTER-VERSION)/\\1${BUILD_NUMBER}\\2/' values.yaml
              """
          }
          sh 'cat values.yaml | grep tag: '
          sh 'git checkout  -b main'
          sh 'git add values.yaml'
          script {
            sh """
              git commit -m "Jenkins: updated dagster tag to ${BUILD_NUMBER} in dagster/base/values.yaml"
            """
           }
          withCredentials([usernamePassword(
            credentialsId: 'mlops-platform-github', 
            passwordVariable: 'GIT_PASSWORD', 
            usernameVariable: "GIT_USERNAME")]) {
              sh "git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/demo125/mlops-platform.git main:main"
          }
        }
      }
    }
  }
}
