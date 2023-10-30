def call(){
    def podTemplate = libraryResource('podTemplate.yaml')
    def prScript = libraryResource "pr.sh"

    pipeline {
        agent {
            kubernetes {
                label "jenkins-${UUID.randomUUID().toString()}"
                yaml "$podTemplate"
            }
        }
        environment {
            NAME = "${jobNameParts[0]}"
            VERSION = "${env.GIT_COMMIT}-${env.BUILD_ID}"
            IMAGE_REPO = "sarthaksatish"
            GITHUB_TOKEN = credentials('githubpat')
            NAMESPACE = "jenkins"
            HELM_CHART_DIRECTORY = "charts/priyankalearnings"
        }

        stages {
            stage('Unit Tests') {
                steps {
                    echo 'Implement unit tests if applicable.'
                    echo 'This stage is a sample placeholder'
                }
            }
        }
    }
}