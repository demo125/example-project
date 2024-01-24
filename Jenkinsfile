pipeline {
  agent {
    kubernetes {
        inheritFrom 'kaniko-pod-template'
    }
  }
  stages {
      stage('Checkout') { 
        steps {
            container('git-container') {
                checkout(
                    [$class: 'GitSCM', 
                    branches: [[name: '*/main']], 
                    doGenerateSubmoduleConfigurations: false, 
                    extensions: [[$class: 'CleanBeforeCheckout']], 
                    submoduleCfg: [], 
                    userRemoteConfigs: [[url: 'https://github.com/demo125/example-project.git']]]
                )
            }
        }
    }
    stage('build image') {
      steps {
        container('kaniko-container') {
            // sh 'executor'
            sh 'ls -la'
            sh "mkdir -p /kaniko/.docker"
            withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', passwordVariable: 'PASSWORD', usernameVariable: 'USER')]) {
                sh "echo '{\"auths\":{\"$DOCKER_REGISTRY_URL\":{\"username\":\"$USER\",\"password\":\"$PASSWORD\"}}}' > /kaniko/.docker/config.json"
                sh 'cat /kaniko/.docker/config.json'
                sh 'executor --context=git://github.com/demo125/example-project.git --dockerfile Dockerfile --destination $DOCKER_REGISTRY_URL/$JOB_BASE_NAME:$BUILD_NUMBER'
            }
            
        }
        // container('busybox') {
        //   sh '/bin/busybox'
        // }
      }
    }
  }
}
